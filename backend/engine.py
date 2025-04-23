from typing import Dict, Optional, List
from backend.models import Country, load_countries_from_file, EconomicModel
import random  # For simple simulation
import math
import datetime
import copy
import json
import numpy as np
from scipy import stats, optimize
import os
import logging
from backend.diplomacy_ai import CountryProfile, Coalition, CoalitionStrategy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiplomacyRelation:
    def __init__(self, country_a, country_b, relation_level=0.0, last_event=None):
        self.country_a = country_a
        self.country_b = country_b
        self.relation_level = relation_level  # -1.0 to 1.0
        self.last_event = last_event

class Alliance:
    def __init__(self, name, members, date_formed, is_active=True, type_="general"):
        self.name = name
        self.members = members  # Liste af ISO-koder
        self.date_formed = date_formed
        self.is_active = is_active
        self.type = type_  # "general", "economic", "military"
        self.date_disbanded = None
    
    def disband(self):
        self.is_active = False
        self.date_disbanded = datetime.date.today().isoformat()
        
def find_relation(relations, country_a, country_b):
    for rel in relations:
        if (rel.country_a == country_a and rel.country_b == country_b) or \
           (rel.country_a == country_b and rel.country_b == country_a):
            return rel
    return None

class HistoricalDataset:
    """
    Represents historical economic data for calibration and benchmarking.
    """
    def __init__(self, data_path=None):
        self.data = {}
        self.global_averages = {}
        self.regional_averages = {}
        self.loaded = False
        if data_path:
            self.load_data(data_path)
    
    def load_data(self, data_path):
        """Load historical data from a JSON file."""
        try:
            if os.path.exists(data_path):
                with open(data_path, encoding='utf-8') as f:
                    self.data = json.load(f)
                self._calculate_averages()
                self.loaded = True
                logger.info(f"Historical data loaded successfully from {data_path}")
            else:
                logger.warning(f"Historical data file not found at {data_path}")
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
    
    def _calculate_averages(self):
        """Calculate global and regional averages for benchmarking."""
        metric_sums = {}
        metric_counts = {}
        regional_data = {}
        
        for country_iso, country_data in self.data.items():
            region = country_data.get('region', 'Unknown')
            if region not in regional_data:
                regional_data[region] = {}
            
            for year, yearly_data in country_data.get('yearly_data', {}).items():
                for metric, value in yearly_data.items():
                    if isinstance(value, (int, float)):
                        if metric not in metric_sums:
                            metric_sums[metric] = {}
                            metric_counts[metric] = {}
                        
                        if year not in metric_sums[metric]:
                            metric_sums[metric][year] = 0
                            metric_counts[metric][year] = 0
                        
                        metric_sums[metric][year] += value
                        metric_counts[metric][year] += 1
                
                if year not in regional_data[region]:
                    regional_data[region][year] = {}
                
                for metric, value in yearly_data.items():
                    if isinstance(value, (int, float)):
                        if metric not in regional_data[region][year]:
                            regional_data[region][year][metric] = []
                        
                        regional_data[region][year][metric].append(value)
        
        for metric, year_data in metric_sums.items():
            self.global_averages[metric] = {}
            for year, total in year_data.items():
                count = metric_counts[metric][year]
                if count > 0:
                    self.global_averages[metric][year] = total / count
        
        for region, years in regional_data.items():
            if region not in self.regional_averages:
                self.regional_averages[region] = {}
            
            for year, metrics in years.items():
                self.regional_averages[region][year] = {}
                for metric, values in metrics.items():
                    if values:
                        self.regional_averages[region][year][metric] = sum(values) / len(values)
    
    def get_historical_data(self, country_iso, start_year=None, end_year=None):
        """Get historical data for a specific country."""
        if country_iso not in self.data:
            logger.warning(f"No historical data found for country: {country_iso}")
            return None
        
        country_data = self.data[country_iso].get('yearly_data', {})
        
        if start_year or end_year:
            filtered_data = {}
            for year_str, data in country_data.items():
                year = int(year_str)
                if (start_year is None or year >= start_year) and (end_year is None or year <= end_year):
                    filtered_data[year_str] = data
            return filtered_data
        
        return country_data
    
    def get_benchmark_data(self, country_iso, metric, years):
        """
        Get benchmark data for a specific country and metric.
        Returns a dict with country, regional, and global values.
        """
        result = {
            'country_values': [],
            'regional_values': [],
            'global_values': []
        }
        
        if not self.loaded or country_iso not in self.data:
            logger.warning(f"No data for benchmarking country: {country_iso}")
            return result
        
        region = self.data[country_iso].get('region', 'Unknown')
        
        for year in years:
            year_str = str(year)
            if year_str in self.data[country_iso].get('yearly_data', {}) and metric in self.data[country_iso]['yearly_data'][year_str]:
                result['country_values'].append(self.data[country_iso]['yearly_data'][year_str][metric])
            else:
                result['country_values'].append(None)
            
            if region in self.regional_averages and year_str in self.regional_averages[region] and metric in self.regional_averages[region][year_str]:
                result['regional_values'].append(self.regional_averages[region][year_str][metric])
            else:
                result['regional_values'].append(None)
            
            if metric in self.global_averages and year_str in self.global_averages[metric]:
                result['global_values'].append(self.global_averages[metric][year_str])
            else:
                result['global_values'].append(None)
        
        return result

class EconomicCalibrator:
    """
    Calibrates economic model parameters based on historical data.
    """
    def __init__(self, historical_data):
        self.historical_data = historical_data
        self.calibration_results = {}
    
    def calibrate_parameters(self, country_iso, model_parameters, target_metrics=None):
        """
        Calibrate economic parameters for a specific country based on historical data.
        """
        if target_metrics is None:
            target_metrics = ['gdp_growth', 'inflation', 'unemployment']
        
        historical_data = self.historical_data.get_historical_data(country_iso)
        if not historical_data:
            logger.warning(f"Cannot calibrate for {country_iso}: No historical data found")
            return model_parameters
        
        historical_series = {}
        for metric in target_metrics:
            historical_series[metric] = []
            for year in sorted(historical_data.keys()):
                if metric in historical_data[year]:
                    historical_series[metric].append(historical_data[year][metric])
        
        for metric, series in historical_series.items():
            if len(series) < 5:
                logger.warning(f"Insufficient historical data for {country_iso} on {metric}")
                return model_parameters
        
        calibration_params = {
            'gdp_growth': ['productivity_factor', 'capital_elasticity', 'labor_elasticity'],
            'inflation': ['monetary_policy_effect', 'phillips_curve_slope'],
            'unemployment': ['natural_rate', 'okun_coefficient']
        }
        
        calibrated_params = model_parameters.copy()
        
        for metric in target_metrics:
            if metric not in calibration_params:
                continue
            
            try:
                params_to_calibrate = calibration_params[metric]
                for param in params_to_calibrate:
                    if param in calibrated_params:
                        calibrated_params[param] = self._optimize_parameter(
                            historical_series[metric], 
                            param, 
                            calibrated_params[param]
                        )
            except Exception as e:
                logger.error(f"Error calibrating {metric} for {country_iso}: {e}")
        
        self.calibration_results[country_iso] = {
            'original_params': model_parameters,
            'calibrated_params': calibrated_params,
            'metrics': target_metrics,
            'data_points': {m: len(historical_series[m]) for m in target_metrics}
        }
        
        logger.info(f"Calibration completed for {country_iso}")
        return calibrated_params
    
    def _optimize_parameter(self, historical_series, param_name, current_value):
        """
        Basic parameter optimization based on historical data.
        """
        mean_value = np.mean(historical_series)
        std_value = np.std(historical_series)
        
        if param_name in ['productivity_factor', 'capital_elasticity', 'labor_elasticity']:
            if mean_value > 3.0:
                return current_value * 1.1
            elif mean_value < 1.0:
                return current_value * 0.9
        
        elif param_name in ['monetary_policy_effect', 'phillips_curve_slope']:
            if std_value > 2.0:
                return current_value * 1.15
            elif std_value < 0.5:
                return current_value * 0.85
        
        elif param_name == 'natural_rate':
            sorted_data = sorted(historical_series)
            natural_rate_estimate = sorted_data[len(sorted_data) // 4]
            return max(3.0, min(8.0, natural_rate_estimate))
        
        return current_value
    
    def get_calibration_report(self, country_iso):
        """Get a report on the calibration process for a country."""
        if country_iso not in self.calibration_results:
            return {"status": "Not calibrated", "message": "No calibration has been performed for this country."}
        
        result = self.calibration_results[country_iso]
        
        param_changes = {}
        for param, new_value in result['calibrated_params'].items():
            if param in result['original_params']:
                old_value = result['original_params'][param]
                change_pct = ((new_value - old_value) / old_value) * 100 if old_value != 0 else float('inf')
                param_changes[param] = {
                    'original': old_value,
                    'calibrated': new_value,
                    'change_pct': change_pct
                }
        
        return {
            "status": "Calibrated",
            "metrics_used": result['metrics'],
            "data_points": result['data_points'],
            "parameter_changes": param_changes,
            "explanation": self._generate_calibration_explanation(country_iso, param_changes)
        }
    
    def _generate_calibration_explanation(self, country_iso, param_changes):
        """Generate a human-readable explanation of calibration changes."""
        if not param_changes:
            return "No parameters were changed during calibration."
        
        explanations = []
        
        growth_params = ['productivity_factor', 'capital_elasticity', 'labor_elasticity']
        inflation_params = ['monetary_policy_effect', 'phillips_curve_slope']
        unemployment_params = ['natural_rate', 'okun_coefficient']
        
        growth_changed = any(param in param_changes for param in growth_params)
        if growth_changed:
            growth_direction = None
            for param in growth_params:
                if param in param_changes and abs(param_changes[param]['change_pct']) > 5:
                    direction = "increased" if param_changes[param]['change_pct'] > 0 else "decreased"
                    if growth_direction is None:
                        growth_direction = direction
                    elif growth_direction != direction:
                        growth_direction = "adjusted"
            
            if growth_direction:
                explanations.append(
                    f"Growth-related parameters were {growth_direction} to better match historical GDP growth patterns."
                )
        
        inflation_changed = any(param in param_changes for param in inflation_params)
        if inflation_changed:
            if 'phillips_curve_slope' in param_changes and abs(param_changes['phillips_curve_slope']['change_pct']) > 5:
                direction = "steeper" if param_changes['phillips_curve_slope']['change_pct'] > 0 else "flatter"
                explanations.append(
                    f"The Phillips curve was adjusted to be {direction}, reflecting the historical relationship "
                    f"between inflation and unemployment in {country_iso}."
                )
        
        if 'natural_rate' in param_changes and abs(param_changes['natural_rate']['change_pct']) > 5:
            new_rate = param_changes['natural_rate']['calibrated']
            explanations.append(
                f"The natural unemployment rate was calibrated to {new_rate:.1f}% based on historical labor market data."
            )
        
        total_params = len(param_changes)
        significant_changes = sum(1 for p in param_changes.values() if abs(p['change_pct']) > 10)
        
        if significant_changes > 0:
            explanations.append(
                f"Overall, {significant_changes} of {total_params} parameters required significant adjustment (>10%) "
                f"to match {country_iso}'s unique economic characteristics."
            )
        else:
            explanations.append(
                f"Overall, the default economic model was already well-suited to {country_iso}'s economic patterns, "
                f"with only minor parameter adjustments needed."
            )
        
        return " ".join(explanations)

class EnhancedFeedbackSystem:
    """
    Provides detailed economic explanations and feedback for game events and decisions.
    Incorporates historical benchmarking and realistic economic analysis.
    """
    def __init__(self, historical_data=None):
        self.historical_data = historical_data
        self.global_context = {}
        self.narrative_templates = self._load_narrative_templates()
    
    def _load_narrative_templates(self):
        """Load narrative templates for various economic situations."""
        return {
            "gdp_growth": {
                "positive": [
                    "The economy is experiencing robust growth, with GDP expanding at {value}% annually.",
                    "Economic activity has strengthened, with GDP growing at {value}% compared to the previous period."
                ],
                "negative": [
                    "The economy is contracting, with GDP shrinking at a rate of {value}% annually.",
                    "Economic activity has weakened significantly, with GDP declining by {value}% compared to the previous period."
                ],
                "neutral": [
                    "The economy is growing steadily at {value}% annually.",
                    "Economic activity is maintaining a moderate pace, with GDP expanding by {value}% compared to the previous period."
                ]
            },
            "inflation": {
                "high": [
                    "Inflation has accelerated to {value}%, significantly above the target range.",
                    "Price pressures are mounting, with inflation reaching {value}% annually."
                ],
                "low": [
                    "Inflation remains subdued at {value}%, below the target range.",
                    "Price pressures are minimal, with inflation at just {value}% annually."
                ],
                "target": [
                    "Inflation is well-contained at {value}%, within the target range.",
                    "Price stability is maintained with inflation at {value}% annually."
                ]
            },
            "trade_balance": {
                "surplus": [
                    "The country is maintaining a strong trade surplus of {value}% of GDP.",
                    "Export competitiveness remains high, leading to a trade surplus of {value}% of GDP."
                ],
                "deficit": [
                    "The country is running a trade deficit of {value}% of GDP.",
                    "Import dependence is reflected in a trade deficit of {value}% of GDP."
                ],
                "balanced": [
                    "Trade flows are roughly balanced, with a small {surplus_or_deficit} of {value}% of GDP.",
                    "The external position is stable with a {surplus_or_deficit} of {value}% of GDP."
                ]
            }
        }
    
    def generate_economic_insight(self, country_data, metric, historical_comparison=True):
        """
        Generate detailed economic insight for a specific metric.
        """
        if metric not in country_data:
            return {"insight": f"No data available for {metric}.", "context": {}}
        
        value = country_data[metric]
        historical_context = {}
        
        if historical_comparison and self.historical_data and 'iso_code' in country_data:
            try:
                recent_years = [datetime.datetime.now().year - i for i in range(1, 6)]
                benchmark = self.historical_data.get_benchmark_data(
                    country_data['iso_code'], 
                    metric, 
                    recent_years
                )
                
                country_values = [v for v in benchmark['country_values'] if v is not None]
                if country_values:
                    historical_context = {
                        'historical_avg': sum(country_values) / len(country_values),
                        'trend': self._calculate_trend(country_values),
                        'country_values': country_values
                    }
                
                regional_values = [v for v in benchmark['regional_values'] if v is not None]
                if regional_values:
                    historical_context['regional_avg'] = sum(regional_values) / len(regional_values)
                    historical_context['relative_to_region'] = value - historical_context['regional_avg']
            
            except Exception as e:
                logger.error(f"Error generating historical context: {e}")
        
        narrative = self._generate_narrative(metric, value, historical_context)
        
        return {
            "insight": narrative,
            "context": historical_context
        }
    
    def _calculate_trend(self, values):
        """Calculate the trend direction from a series of values."""
        if len(values) < 2:
            return "stable"
        
        x = list(range(len(values)))
        slope, _, _, _, _ = stats.linregress(x, values)
        
        if abs(slope) < 0.1:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def _generate_narrative(self, metric, value, historical_context):
        """Generate a narrative description based on the metric and context."""
        if metric == 'gdp_growth':
            return self._generate_gdp_growth_narrative(value, historical_context)
        elif metric == 'inflation':
            return self._generate_inflation_narrative(value, historical_context)
        elif metric == 'unemployment':
            return self._generate_unemployment_narrative(value, historical_context)
        elif metric == 'trade_balance':
            return self._generate_trade_balance_narrative(value, historical_context)
        else:
            return f"The {metric.replace('_', ' ')} is currently at {value}."
    
    def _generate_gdp_growth_narrative(self, value, historical_context):
        """Generate narrative for GDP growth."""
        if value > 3.0:
            template_key = "positive"
        elif value < 0:
            template_key = "negative"
            value = abs(value)
        else:
            template_key = "neutral"
        
        templates = self.narrative_templates["gdp_growth"][template_key]
        base_narrative = random.choice(templates).format(value=value)
        
        if historical_context:
            historical_avg = historical_context.get('historical_avg')
            regional_avg = historical_context.get('regional_avg')
            trend = historical_context.get('trend')
            
            if historical_avg is not None:
                comparison = f"This compares to a {historical_avg:.1f}% historical average "
                if trend == "increasing":
                    comparison += "with an improving trend over recent years."
                elif trend == "decreasing":
                    comparison += "with a declining trend over recent years."
                else:
                    comparison += "which has been relatively stable in recent years."
                
                base_narrative += f" {comparison}"
            
            if regional_avg is not None:
                rel_to_region = value - regional_avg
                if abs(rel_to_region) < 0.5:
                    regional_comparison = f"This is in line with the regional average of {regional_avg:.1f}%."
                elif rel_to_region > 0:
                    regional_comparison = f"This is {rel_to_region:.1f} percentage points above the regional average of {regional_avg:.1f}%."
                else:
                    regional_comparison = f"This is {abs(rel_to_region):.1f} percentage points below the regional average of {regional_avg:.1f}%."
                
                base_narrative += f" {regional_comparison}"
        
        return base_narrative
    
    def _generate_inflation_narrative(self, value, historical_context):
        """Generate narrative for inflation."""
        if value > 5.0:
            template_key = "high"
        elif value < 1.0:
            template_key = "low"
        else:
            template_key = "target"
        
        templates = self.narrative_templates["inflation"][template_key]
        base_narrative = random.choice(templates).format(value=value)
        
        if historical_context:
            historical_avg = historical_context.get('historical_avg')
            
            if historical_avg is not None:
                difference = value - historical_avg
                if abs(difference) < 0.3:
                    base_narrative += f" This is consistent with the historical average of {historical_avg:.1f}%."
                elif difference > 0:
                    base_narrative += f" This represents an increase from the historical average of {historical_avg:.1f}%."
                else:
                    base_narrative += f" This represents a decrease from the historical average of {historical_avg:.1f}%."
        
        return base_narrative
    
    def _generate_unemployment_narrative(self, value, historical_context):
        """Generate narrative for unemployment rate."""
        if value < 4.0:
            base_narrative = f"The labor market is tight with unemployment at just {value:.1f}%."
        elif value > 8.0:
            base_narrative = f"The labor market is showing significant slack with unemployment at {value:.1f}%."
        else:
            base_narrative = f"The unemployment rate stands at {value:.1f}%, indicating a balanced labor market."
        
        if historical_context and 'historical_avg' in historical_context:
            hist_avg = historical_context['historical_avg']
            difference = value - hist_avg
            
            if abs(difference) < 0.5:
                base_narrative += f" This is close to the historical norm of {hist_avg:.1f}%."
            elif difference > 0:
                base_narrative += f" This is above the historical average of {hist_avg:.1f}%, suggesting deteriorating labor market conditions."
            else:
                base_narrative += f" This is below the historical average of {hist_avg:.1f}%, indicating improving labor market conditions."
        
        return base_narrative
    
    def _generate_trade_balance_narrative(self, value, historical_context):
        """Generate narrative for trade balance."""
        hist_avg = historical_context.get('average', 0)
        hist_min = historical_context.get('min', -5)
        hist_max = historical_context.get('max', 5)
        trend = historical_context.get('trend', 'stable')
        
        # Get the narrative based on the current value
        if value > 0:
            base_narrative = f"The trade balance is positive at {value:.1f}% of GDP, indicating a trade surplus."
            if value > hist_avg * 1.5:
                base_narrative += " This is a significantly strong trade position."
            elif value > hist_avg:
                base_narrative += " This is above the historical average, showing a healthy external position."
        elif value < 0:
            base_narrative = f"The trade balance is negative at {value:.1f}% of GDP, indicating a trade deficit."
            if value < hist_min * 0.8:
                base_narrative += " This deficit is substantially larger than historical norms and may require attention."
            elif value < hist_avg:
                base_narrative += " This is below the historical average, suggesting potential competitiveness issues."
        else:
            base_narrative = "The trade balance is balanced (0% of GDP), indicating equal exports and imports."
        
        # Add trend context
        if trend == 'improving':
            base_narrative += " The trend is improving, showing strengthening trade competitiveness."
        elif trend == 'deteriorating':
            base_narrative += " The trend is deteriorating, suggesting declining export competitiveness or increasing import dependency."
        
        # Add policy implications
        if value < -3:
            base_narrative += " Policy options might include export promotion, currency depreciation, or import substitution strategies."
        elif value > 5:
            base_narrative += " While a surplus is positive, an excessively high surplus might indicate underinvestment in the domestic economy."
        
        return base_narrative
        
    def generate_comparison_report(self, country_iso, metrics):
        """
        Generate a comprehensive report comparing current economic metrics with historical benchmarks.
        
        Args:
            country_iso: ISO code for the country
            metrics: List of metrics to include in the report
            
        Returns:
            Dictionary with comparison narratives for each metric
        """
        if not self.historical_data or not self.historical_data.loaded:
            return {"status": "No historical data available for comparison"}
        
        report = {}
        recent_years = list(range(2010, 2023))  # Adjust this range based on available data
        
        for metric in metrics:
            benchmark_data = self.historical_data.get_benchmark_data(country_iso, metric, recent_years)
            
            # Filter out None values
            country_values = [v for v in benchmark_data['country_values'] if v is not None]
            regional_values = [v for v in benchmark_data['regional_values'] if v is not None]
            global_values = [v for v in benchmark_data['global_values'] if v is not None]
            
            if not country_values:
                report[metric] = "Insufficient historical data for comparison"
                continue
            
            country_avg = sum(country_values) / len(country_values) if country_values else 0
            regional_avg = sum(regional_values) / len(regional_values) if regional_values else 0
            global_avg = sum(global_values) / len(global_values) if global_values else 0
            
            narrative = f"Historical {metric} analysis:\n"
            
            # Country historical performance
            narrative += f"- Historical average for this country: {country_avg:.2f}%\n"
            if len(country_values) >= 2:
                if country_values[-1] > country_values[0]:
                    narrative += f"- Long-term trend: Increasing (from {country_values[0]:.2f}% to {country_values[-1]:.2f}%)\n"
                elif country_values[-1] < country_values[0]:
                    narrative += f"- Long-term trend: Decreasing (from {country_values[0]:.2f}% to {country_values[-1]:.2f}%)\n"
                else:
                    narrative += "- Long-term trend: Stable\n"
            
            # Regional and global comparison
            if regional_values:
                narrative += f"- Regional average: {regional_avg:.2f}%"
                if country_avg > regional_avg:
                    narrative += f" (Country performs {country_avg - regional_avg:.2f}% better than region)\n"
                else:
                    narrative += f" (Country performs {regional_avg - country_avg:.2f}% worse than region)\n"
            
            if global_values:
                narrative += f"- Global average: {global_avg:.2f}%"
                if country_avg > global_avg:
                    narrative += f" (Country performs {country_avg - global_avg:.2f}% better than global average)\n"
                else:
                    narrative += f" (Country performs {global_avg - country_avg:.2f}% worse than global average)\n"
            
            report[metric] = narrative
        
        return report

def _generate_turn_summary(self, country_iso):
    """Generate a summary of the turn for the given country."""
    country = self.countries[country_iso]
    
    summary = f"Turn {self.current_turn} Summary for {country.get('name', country_iso)}:\n\n"
    
    # Economic indicators summary
    economic_summary = []
    
    if hasattr(country, 'gdp_growth'):
        economic_summary.append(f"GDP Growth: {country.gdp_growth:.1f}%")
    
    if hasattr(country, 'inflation'):
        economic_summary.append(f"Inflation: {country.inflation:.1f}%")
        
    if hasattr(country, 'unemployment'):
        economic_summary.append(f"Unemployment: {country.unemployment:.1f}%")
        
    if hasattr(country, 'trade_balance'):
        economic_summary.append(f"Trade Balance: {country.trade_balance:.1f}% of GDP")
    
    if economic_summary:
        summary += "Economic Indicators:\n- " + "\n- ".join(economic_summary) + "\n\n"
    
    # Historical context if available
    if self.historical_data and self.historical_data.loaded:
        try:
            metrics_to_compare = ['gdp_growth', 'inflation', 'unemployment', 'trade_balance']
            available_metrics = [m for m in metrics_to_compare if hasattr(country, m)]
            
            if available_metrics:
                historical_report = self.feedback_system.generate_comparison_report(
                    country_iso,
                    available_metrics
                )
                
                if historical_report and not isinstance(historical_report, dict) or 'status' not in historical_report:
                    summary += "Historical Benchmarking:\n"
                    for metric, report in historical_report.items():
                        if isinstance(report, str) and "Insufficient" not in report:
                            summary += f"{report}\n\n"
        except Exception as e:
            logger.error(f"Error generating historical summary: {e}")
    
    # Policy consequences summary
    if hasattr(country, 'policy_effects'):
        summary += "Policy Effects:\n"
        for policy, effect in country.policy_effects.items():
            summary += f"- {policy}: {effect}\n"
        summary += "\n"
    
    # Diplomatic status summary
    if hasattr(self, 'diplomacy') and hasattr(self.diplomacy, 'get_diplomatic_overview'):
        diplomatic_status = self.diplomacy.get_diplomatic_overview(country_iso)
        if diplomatic_status:
            summary += "Diplomatic Status:\n"
            for relation in diplomatic_status[:5]:  # Show top 5 relations
                summary += f"- {relation['country']}: {relation['status']} (Score: {relation['score']})\n"
            summary += "\n"
    
    # Active events
    active_events = self.event_manager.get_active_events()
    if active_events:
        summary += "Active Events:\n"
        for event in active_events:
            turns_remaining = event.duration - (self.current_turn - event.start_turn)
            summary += f"- {event.name} ({turns_remaining} turns remaining)\n"
        summary += "\n"
    
    # Add recommendations
    recommendations = self._generate_policy_recommendations(country_iso)
    if recommendations:
        summary += "Recommendations:\n"
        for rec in recommendations[:3]:  # Top 3 recommendations
            summary += f"- {rec}\n"
    
    return summary

class BudgetManager:
    """
    Handles the government budget and subsidy management for countries in the simulation.
    """
    def __init__(self, economic_model):
        self.economic_model = economic_model
    
    def calculate_budget(self, country):
        """
        Calculate the country's budget based on its economic status.
        Estimates revenues and updates budget balance.
        """
        # GDP-based revenue calculation (simplified)
        tax_rate = self._get_effective_tax_rate(country)
        country.budget['revenue']['taxation'] = country.gdp * tax_rate
        
        # Calculate tariff revenue
        tariff_revenue = 0.0
        for partner_iso, trade_data in country.trade_partners.items():
            imports = trade_data.get('imports', 0.0)
            if partner_iso in country.tariffs:
                # Apply tariff rates to imports from this country
                for category, rate in country.tariffs[partner_iso].items():
                    # Estimate the proportion of this category in total imports
                    # For simplicity, we'll use the industry breakdown
                    if category == 'manufacturing':
                        proportion = country.industries.manufacturing
                    elif category == 'agriculture':
                        proportion = country.industries.agriculture
                    elif category == 'services':
                        proportion = country.industries.services
                    else:
                        proportion = 0.1  # Default for other categories
                    
                    tariff_revenue += imports * proportion * rate
        
        country.budget['revenue']['tariffs'] = tariff_revenue
        
        # Update total revenue
        total_revenue = sum(country.budget['revenue'].values())
        
        # Update balance (revenue - expenses)
        total_expenses = sum(country.budget['expenses'].values())
        country.budget['balance'] = total_revenue - total_expenses
        
        # Update debt and debt-to-GDP ratio if balance is negative
        if country.budget['balance'] < 0:
            country.budget['debt'] += abs(country.budget['balance'])
        
        # Calculate debt-to-GDP ratio
        if country.gdp > 0:
            country.budget['debt_to_gdp_ratio'] = (country.budget['debt'] / country.gdp) * 100
        
        return country.budget
    
    def _get_effective_tax_rate(self, country):
        """
        Determine an appropriate tax rate based on government type and other factors.
        """
        # Base rates by government type (simplified)
        base_rates = {
            'democracy': 0.35,
            'republic': 0.33,
            'monarchy': 0.38,
            'dictatorship': 0.40,
            'communist': 0.45,
            'socialist': 0.42
        }
        
        # Default rate if government type is not recognized
        base_rate = base_rates.get(country.government_type.lower(), 0.35)
        
        # Adjust for economic conditions
        if country.unemployment_rate > 10:
            base_rate -= 0.03  # Lower tax rate for high unemployment
        elif country.unemployment_rate < 4:
            base_rate += 0.02  # Higher tax rate for strong employment
        
        if country.growth_rate < 0:
            base_rate -= 0.04  # Lower taxes during recession
        elif country.growth_rate > 3:
            base_rate += 0.02  # Higher taxes during strong growth
        
        # Ensure the rate stays within reasonable bounds
        return max(0.15, min(0.5, base_rate))
    
    def manage_subsidies(self, country, sector_name, subsidy_percentage):
        """
        Apply subsidies to a specific sector and calculate the economic effects.
        
        Args:
            country: The Country object
            sector_name: Name of the sector to subsidize
            subsidy_percentage: Percentage of sector output to subsidize (0-100)
        
        Returns:
            A dictionary with the effects of the subsidy
        """
        # Verify subsidy percentage is valid
        subsidy_percentage = max(0, min(100, subsidy_percentage))
        subsidy_fraction = subsidy_percentage / 100.0
        
        # Find the sector
        target_sector = None
        for sector in country.sectors:
            if sector.name.lower() == sector_name.lower():
                target_sector = sector
                break
        
        if not target_sector:
            return {"error": f"Sector '{sector_name}' not found"}
        
        # Calculate subsidy amount based on sector output
        subsidy_amount = target_sector.output * subsidy_fraction
        
        # Store subsidy information
        country.subsidies[sector_name] = {
            'amount': subsidy_amount,
            'percentage': subsidy_percentage,
            'effects': {}
        }
        
        # Update budget expenses
        country.budget['expenses']['subsidies'] += subsidy_amount
        
        # Calculate economic effects
        # 1. Production effect: Subsidies can increase output
        output_boost = subsidy_amount * 0.7  # 70% efficiency in converting subsidies to output
        original_output = target_sector.output
        target_sector.output += output_boost
        
        # 2. Employment effect: Subsidies can reduce unemployment in the sector
        employment_boost_percentage = subsidy_fraction * 0.5  # Half of subsidy percentage goes to employment
        original_unemployment = target_sector.unemployment_rate
        new_unemployment = max(0, target_sector.unemployment_rate - employment_boost_percentage)
        target_sector.unemployment_rate = new_unemployment
        
        # 3. Price effect: Subsidies can reduce prices
        price_reduction = subsidy_fraction * 0.3  # 30% of subsidy percentage goes to price reduction
        original_price = target_sector.price
        target_sector.price *= (1 - price_reduction)
        
        # 4. Export competitiveness: Lower prices can boost exports
        export_boost = 0
        if subsidy_percentage > 5:  # Only significant subsidies affect exports
            export_boost_percentage = price_reduction * 1.5  # Price reduction has leveraged effect on exports
            original_export = target_sector.export
            export_boost = target_sector.export * export_boost_percentage
            target_sector.export += export_boost
        
        # Store effects for reporting
        effects = {
            'output_increase': output_boost,
            'output_increase_percentage': (output_boost / original_output) * 100 if original_output > 0 else 0,
            'unemployment_reduction': original_unemployment - new_unemployment,
            'price_reduction_percentage': price_reduction * 100,
            'export_increase': export_boost
        }
        
        country.subsidies[sector_name]['effects'] = effects
        
        # Recalculate country-level metrics
        country.gdp = self.economic_model.aggregate_gdp(country)
        country.unemployment_rate = self.economic_model.aggregate_unemployment(country)
        
        # Recalculate budget with the new expenses
        self.calculate_budget(country)
        
        return effects
    
    def remove_subsidy(self, country, sector_name):
        """
        Remove subsidies from a specific sector and recalculate economic effects.
        
        Args:
            country: The Country object
            sector_name: Name of the sector to remove subsidy from
        
        Returns:
            A dictionary with the economic effects of removing the subsidy
        """
        if sector_name not in country.subsidies:
            return {"error": f"No subsidy found for sector '{sector_name}'"}
        
        # Get subsidy details
        subsidy = country.subsidies[sector_name]
        subsidy_amount = subsidy['amount']
        
        # Find the sector
        target_sector = None
        for sector in country.sectors:
            if sector.name.lower() == sector_name.lower():
                target_sector = sector
                break
        
        if not target_sector:
            return {"error": f"Sector '{sector_name}' not found"}
        
        # Reverse the economic effects
        effects = subsidy['effects']
        
        # 1. Reverse production effect
        if 'output_increase' in effects:
            target_sector.output -= effects['output_increase']
        
        # 2. Reverse employment effect
        if 'unemployment_reduction' in effects:
            target_sector.unemployment_rate += effects['unemployment_reduction']
        
        # 3. Reverse price effect
        if 'price_reduction_percentage' in effects:
            price_increase_factor = 1 / (1 - effects['price_reduction_percentage'] / 100)
            target_sector.price *= price_increase_factor
        
        # 4. Reverse export effect
        if 'export_increase' in effects:
            target_sector.export -= effects['export_increase']
        
        # Update budget expenses
        country.budget['expenses']['subsidies'] -= subsidy_amount
        
        # Remove the subsidy
        removed_subsidy = country.subsidies.pop(sector_name)
        
        # Recalculate country-level metrics
        country.gdp = self.economic_model.aggregate_gdp(country)
        country.unemployment_rate = self.economic_model.aggregate_unemployment(country)
        
        # Recalculate budget with the updated expenses
        self.calculate_budget(country)
        
        return {
            "message": f"Subsidy removed from {sector_name}",
            "removed_amount": subsidy_amount,
            "prior_effects": removed_subsidy['effects']
        }
    
    def adjust_budget_allocation(self, country, category, amount):
        """
        Adjust budget allocation for a specific expense category.
        
        Args:
            country: The Country object
            category: Budget category to adjust (e.g., 'defense', 'education')
            amount: New amount to allocate (absolute value)
        
        Returns:
            Updated budget information
        """
        if category not in country.budget['expenses']:
            return {"error": f"Budget category '{category}' not found"}
        
        # Store the original amount for reporting
        original_amount = country.budget['expenses'][category]
        
        # Update the budget allocation
        country.budget['expenses'][category] = amount
        
        # Recalculate budget balance
        self.calculate_budget(country)
        
        # Calculate effects based on the category
        effects = self._calculate_budget_allocation_effects(country, category, original_amount, amount)
        
        return {
            "message": f"Budget for {category} adjusted from {original_amount} to {amount}",
            "prior_amount": original_amount,
            "new_amount": amount,
            "effects": effects,
            "budget_balance": country.budget['balance']
        }
    
    def _calculate_budget_allocation_effects(self, country, category, old_amount, new_amount):
        """
        Calculate the economic effects of changing budget allocations.
        
        Different categories have different effects on the economy.
        """
        effects = {}
        change = new_amount - old_amount
        change_percentage = (change / old_amount) * 100 if old_amount > 0 else 0
        
        if category == 'education':
            # Education affects long-term productivity and growth
            if change > 0:
                effects['long_term_growth'] = min(0.5, change_percentage * 0.01)
                effects['description'] = "Increased education spending will boost long-term economic growth."
            else:
                effects['long_term_growth'] = max(-0.5, change_percentage * 0.01)
                effects['description'] = "Decreased education spending may reduce long-term economic growth."
        
        elif category == 'healthcare':
            # Healthcare affects population welfare and productivity
            if change > 0:
                effects['productivity'] = min(0.3, change_percentage * 0.005)
                effects['description'] = "Improved healthcare spending will increase workforce productivity."
            else:
                effects['productivity'] = max(-0.3, change_percentage * 0.005)
                effects['description'] = "Reduced healthcare spending may decrease workforce productivity."
        
        elif category == 'infrastructure':
            # Infrastructure affects production capacity and efficiency
            if change > 0:
                effects['capacity_increase'] = min(1.0, change_percentage * 0.02)
                effects['description'] = "Infrastructure investment will increase production capacity."
            else:
                effects['capacity_decrease'] = min(1.0, abs(change_percentage) * 0.01)
                effects['description'] = "Reduced infrastructure spending may limit production capacity."
        
        elif category == 'defense':
            # Defense affects national security and diplomatic leverage
            if change > 0:
                effects['diplomatic_strength'] = min(2.0, change_percentage * 0.04)
                effects['description'] = "Increased defense spending enhances diplomatic position."
            else:
                effects['diplomatic_strength'] = max(-2.0, change_percentage * 0.04)
                effects['description'] = "Decreased defense spending may weaken diplomatic position."
        
        elif category == 'social_services':
            # Social services affect population welfare and inequality
            if change > 0:
                effects['approval_rating'] = min(2.0, change_percentage * 0.05)
                effects['description'] = "Increased social spending improves public approval."
            else:
                effects['approval_rating'] = max(-3.0, change_percentage * 0.07)
                effects['description'] = "Cuts to social spending may significantly decrease public approval."
                
            # Apply immediate effect to approval rating
            country.approval_rating = max(0, min(100, country.approval_rating + effects.get('approval_rating', 0)))
        
        return effects

class GameEngine:
    """
    Main game engine for managing the simulation.
    """
    def __init__(self, scenario=None):
        self.scenario = scenario
        self.countries = {}
        self.current_turn = 0
        self.historical_data = HistoricalDataset()
        self.feedback_system = EnhancedFeedbackSystem(self.historical_data)
        self.ai_explanation_system = None
        self.ai_decisions_history = []
        self.diplomacy = None
        self.diplomatic_consequence = None  # Holder for diplomatic consequence system
        self.country_strategies = {}  # Dict to hold country-specific coalition strategies
    
    def initialize_diplomacy(self):
        """Initialize diplomacy system for the game."""
        # Initialize basic diplomacy system
        self.diplomacy = DiplomacyAI(self)
        
        # Initialize diplomatic consequence system
        self.diplomatic_consequence = DiplomaticConsequence(self)
        
        # Create coalition strategies for each country
        self._initialize_coalition_strategies()
        
        return self.diplomacy
    
    def _initialize_coalition_strategies(self):
        """Initialize coalition strategies for each country based on their profiles."""
        for country_iso, country in self.countries.items():
            # Create or retrieve country profile
            if hasattr(country, 'profile'):
                profile = country.profile
            else:
                profile = self.get_country_profile(country_iso)
                
            # Create country's coalition strategy
            self.country_strategies[country_iso] = CoalitionStrategy(country_iso, profile)
    
    def get_country_profile(self, country_iso):
        """Retrieve the country profile for AI decision explanations."""
        if country_iso not in self.countries:
            return None
            
        if hasattr(self.countries[country_iso], 'profile'):
            return self.countries[country_iso].profile
            
        # Create a new profile if none exists
        profile = CountryProfile()
        # Populate with country-specific values based on existing data
        country = self.countries[country_iso]
        
        if hasattr(country, 'government_type'):
            # Set profile attributes based on government type
            if country.government_type.lower() in ['democracy', 'republic']:
                profile.economic_focus = 0.6
                profile.isolationism = 0.3
                profile.aggression = 0.3
            elif country.government_type.lower() in ['dictatorship', 'authoritarian']:
                profile.economic_focus = 0.5
                profile.isolationism = 0.5
                profile.aggression = 0.6
                
        # Assign the profile to the country
        self.countries[country_iso].profile = profile
        return profile
    
    def evaluate_coalition_opportunities(self, country_iso=None):
        """
        Evaluate opportunities for creating or joining coalitions.
        
        Args:
            country_iso: Optional ISO code to evaluate for specific country only
            
        Returns:
            Dictionary of coalition opportunities
        """
        opportunities = {}
        
        # If specific country is provided, evaluate only for that country
        if country_iso:
            if country_iso in self.country_strategies:
                strategy = self.country_strategies[country_iso]
                country_opportunities = strategy.evaluate_potential_coalitions(self)
                opportunities[country_iso] = country_opportunities
        else:
            # Evaluate for all countries with strategies
            for iso, strategy in self.country_strategies.items():
                country_opportunities = strategy.evaluate_potential_coalitions(self)
                opportunities[iso] = country_opportunities
        
        return opportunities
    
    def decide_coalition_actions(self, country_iso=None):
        """
        Decide what coalition actions countries should take.
        
        Args:
            country_iso: Optional ISO code to decide actions for specific country only
            
        Returns:
            Dictionary of decisions by country
        """
        decisions = {}
        
        # If specific country is provided, decide only for that country
        if country_iso:
            if country_iso in self.country_strategies:
                strategy = self.country_strategies[country_iso]
                decision = strategy.decide_coalition_action(self)
                decisions[country_iso] = decision
                # Process the decision
                self._process_coalition_decision(country_iso, decision)
        else:
            # Decide for all countries with strategies
            for iso, strategy in self.country_strategies.items():
                decision = strategy.decide_coalition_action(self)
                decisions[iso] = decision
                # Process the decision
                self._process_coalition_decision(iso, decision)
        
        return decisions
    
    def _process_coalition_decision(self, country_iso, decision):
        """
        Process a coalition decision from an AI country.
        
        Args:
            country_iso: ISO code of the country making the decision
            decision: Dictionary containing the decision details
        """
        action = decision.get('action')
        
        if action == 'form_coalition':
            # Extract coalition details
            coalition_data = decision.get('coalition_data', {})
            if coalition_data and 'candidates' in coalition_data and 'purpose' in coalition_data:
                # Propose the coalition
                proposal = self.diplomacy.propose_coalition(
                    country_iso,
                    coalition_data['purpose'],
                    coalition_data['candidates'],
                    self.current_turn
                )
                
                # Record the proposal in the decision
                decision['proposal_id'] = proposal['id']
                
                # AI countries respond to the proposal
                for candidate in coalition_data['candidates']:
                    if candidate != country_iso and candidate in self.country_strategies:
                        # Have the AI country evaluate and respond to the proposal
                        candidate_strategy = self.country_strategies[candidate]
                        accept = candidate_strategy.evaluate_coalition_proposal(proposal, self) > 0.5
                        self.diplomacy.respond_to_coalition_proposal(
                            candidate, 
                            proposal['id'], 
                            accept, 
                            self.current_turn
                        )
        
        elif action == 'join_coalition':
            coalition_id = decision.get('coalition_id')
            if coalition_id and hasattr(self.diplomacy, 'coalitions'):
                for coalition in self.diplomacy.coalitions:
                    if coalition.id == coalition_id:
                        success = coalition.add_country(country_iso, self.current_turn)
                        decision['success'] = success
                        
                        # Calculate diplomatic consequences
                        if success and self.diplomatic_consequence:
                            effects = self.diplomatic_consequence.calculate_coalition_action_effects(
                                coalition,
                                {'type': 'member_joined', 'country': country_iso},
                                self
                            )
                            # Apply the effects
                            self.diplomatic_consequence.apply_effects(effects, self)
                        break
        
        elif action == 'leave_coalition':
            coalition_id = decision.get('coalition_id')
            reason = decision.get('reason', 'strategic_decision')
            
            if coalition_id and hasattr(self.diplomacy, 'coalitions'):
                for coalition in self.diplomacy.coalitions:
                    if coalition.id == coalition_id:
                        success = coalition.remove_country(country_iso, self.current_turn)
                        decision['success'] = success
                        
                        # Calculate diplomatic consequences
                        if success and self.diplomatic_consequence:
                            effects = self.diplomatic_consequence.calculate_coalition_action_effects(
                                coalition,
                                {'type': 'member_left', 'country': country_iso, 'reason': reason},
                                self
                            )
                            # Apply the effects
                            self.diplomatic_consequence.apply_effects(effects, self)
                        break
        
        elif action == 'challenge_leadership':
            coalition_id = decision.get('coalition_id')
            
            if coalition_id and hasattr(self.diplomacy, 'coalitions'):
                for coalition in self.diplomacy.coalitions:
                    if coalition.id == coalition_id and country_iso in coalition.member_countries:
                        # Determine success chance based on member influence
                        challenger_influence = coalition.get_member_influence(country_iso, self)
                        leader_influence = coalition.get_member_influence(coalition.leader_country, self)
                        
                        success_threshold = 0.6  # Challenger needs 60% of leader's influence
                        
                        if challenger_influence > leader_influence * success_threshold:
                            outcome = 'success'
                            old_leader = coalition.leader_country
                            coalition.leader_country = country_iso
                        elif challenger_influence > leader_influence * 0.4:  # Close but not enough
                            outcome = 'compromise'
                        else:
                            outcome = 'failure'
                            
                        decision['outcome'] = outcome
                        
                        # Calculate diplomatic consequences of leadership challenge
                        if self.diplomatic_consequence:
                            effects = self.diplomatic_consequence.calculate_leadership_challenge_effects(
                                coalition,
                                country_iso,
                                outcome,
                                self
                            )
                            # Apply the effects
                            self.diplomatic_consequence.apply_effects(effects, self)
                        break
        
        elif action == 'propose_coalition_action':
            coalition_id = decision.get('coalition_id')
            proposed_action = decision.get('proposed_action', {})
            
            if coalition_id and hasattr(self.diplomacy, 'coalitions') and proposed_action:
                for coalition in self.diplomacy.coalitions:
                    if coalition.id == coalition_id and country_iso in coalition.member_countries:
                        # Leader has more weight in proposal acceptance
                        is_leader = country_iso == coalition.leader_country
                        
                        # Determine if action is approved by coalition members
                        approval_threshold = 0.6  # 60% of members need to approve
                        
                        # Simple simulation of member approval
                        approving_members = 0
                        for member in coalition.member_countries:
                            if member == country_iso:
                                approving_members += 1  # Proposer always agrees
                            elif member in self.country_strategies:
                                # Have AI evaluate the proposed action
                                member_strategy = self.country_strategies[member]
                                if member_strategy.evaluate_coalition_action(proposed_action, coalition, self) > 0.5:
                                    approving_members += 1
                        
                        approval_rate = approving_members / len(coalition.member_countries)
                        action_approved = approval_rate >= approval_threshold
                        
                        if action_approved:
                            # Record the action in coalition history
                            coalition.record_action(
                                proposed_action.get('type', 'unknown'),
                                proposed_action,
                                self.current_turn
                            )
                            
                            # Calculate diplomatic consequences
                            if self.diplomatic_consequence:
                                effects = self.diplomatic_consequence.calculate_coalition_action_effects(
                                    coalition,
                                    proposed_action,
                                    self
                                )
                                # Apply the effects
                                self.diplomatic_consequence.apply_effects(effects, self)
                        
                        decision['action_approved'] = action_approved
                        decision['approval_rate'] = approval_rate
                        break
        
        # Record the decision and explanation in AI decisions history
        self.process_ai_country_decision(country_iso, 'coalition', decision)
    
    def get_coalition_report(self, country_iso=None):
        """
        Generate a report on coalition activities and statuses.
        
        Args:
            country_iso: Optional ISO code to get report specific to a country
            
        Returns:
            Dictionary with coalition report information
        """
        report = {
            'active_coalitions': [],
            'coalition_proposals': [],
            'recent_actions': [],
            'diplomatic_effects': []
        }
        
        # Get active coalitions
        if hasattr(self.diplomacy, 'coalitions'):
            active_coalitions = []
            
            for coalition in self.diplomacy.coalitions:
                # If country_iso is specified, only include coalitions that country is part of
                if country_iso and country_iso not in coalition.member_countries:
                    continue
                    
                # Coalition data
                coalition_data = {
                    'id': coalition.id,
                    'name': coalition.name,
                    'purpose': coalition.purpose,
                    'leader': coalition.leader_country,
                    'members': list(coalition.member_countries),
                    'formation_turn': coalition.formation_turn,
                    'cohesion': coalition.cohesion_level,
                    'is_active': coalition.is_active(self.current_turn)
                }
                
                active_coalitions.append(coalition_data)
            
            report['active_coalitions'] = active_coalitions
        
        # Get coalition proposals
        if hasattr(self.diplomacy, 'coalition_proposals'):
            proposals = []
            
            for proposal_id, proposal in self.diplomacy.coalition_proposals.items():
                # If country_iso is specified, only include proposals relevant to that country
                if country_iso and country_iso != proposal['proposing_country'] and country_iso not in proposal['candidate_countries']:
                    continue
                    
                # Only include active (not expired) proposals
                if proposal['status'] == 'pending':
                    proposal_data = {
                        'id': proposal_id,
                        'name': proposal.get('coalition_name', 'Unnamed Coalition'),
                        'proposer': proposal['proposing_country'],
                        'purpose': proposal['purpose'],
                        'candidates': proposal['candidate_countries'],
                        'proposal_turn': proposal['proposal_turn'],
                        'responses': proposal.get('responses', {})
                    }
                    
                    proposals.append(proposal_data)
            
            report['coalition_proposals'] = proposals
        
        # Get recent coalition actions
        if hasattr(self.diplomacy, 'coalitions'):
            recent_actions = []
            
            for coalition in self.diplomacy.coalitions:
                # If country_iso is specified, only include actions from coalitions that country is part of
                if country_iso and country_iso not in coalition.member_countries:
                    continue
                    
                # Get recent actions (last 5 turns)
                for action in coalition.actions_history:
                    if action['turn'] > self.current_turn - 5:
                        action_data = {
                            'coalition': coalition.name,
                            'type': action['type'],
                            'turn': action['turn'],
                            'details': action['details']
                        }
                        
                        recent_actions.append(action_data)
            
            report['recent_actions'] = recent_actions
        
        # Get diplomatic effects if country is specified
        if country_iso and self.diplomatic_consequence:
            report['diplomatic_effects'] = self.diplomatic_consequence.generate_effect_report(
                country_iso, 
                self.current_turn
            )
        
        return report
    
    def update_coalition_dynamics(self):
        """
        Update coalition dynamics including cohesion, actions, and diplomatic effects.
        This should be called at the end of each turn.
        
        Returns:
            List of events that occurred during the update
        """
        events = []
        
        # Update all coalitions
        if hasattr(self.diplomacy, 'coalitions'):
            # First, let the coalition system do its internal updates
            coalition_events = self.diplomacy.update_coalitions(self.current_turn)
            events.extend(coalition_events)
            
            # Then apply diplomatic consequences of those events
            if self.diplomatic_consequence:
                for event in coalition_events:
                    if event['type'] == 'coalition_dissolved':
                        # Find the coalition that was dissolved
                        for coalition in self.diplomacy.coalitions:
                            if coalition.name == event['coalition']:
                                effects = self.diplomatic_consequence.calculate_coalition_dissolution_effects(
                                    coalition,
                                    event['reason'],
                                    self
                                )
                                # Apply the effects
                                self.diplomatic_consequence.apply_effects(effects, self)
                                break
                    elif event['type'] == 'leadership_change':
                        # Find the coalition that experienced leadership change
                        for coalition in self.diplomacy.coalitions:
                            if coalition.name == event['coalition']:
                                effects = self.diplomatic_consequence.calculate_leadership_change_effects(
                                    coalition,
                                    event['old_leader'],
                                    event['new_leader'],
                                    event['reason'],
                                    self
                                )
                                # Apply the effects
                                self.diplomatic_consequence.apply_effects(effects, self)
                                break
                    elif event['type'] == 'cohesion_change':
                        # Find the coalition that experienced significant cohesion change
                        for coalition in self.diplomacy.coalitions:
                            if coalition.name == event['coalition']:
                                # Only calculate consequences for significant changes
                                if abs(event['change']) >= 0.15:
                                    effects = self.diplomatic_consequence.calculate_cohesion_change_effects(
                                        coalition,
                                        event['change'],
                                        event['reason'],
                                        self
                                    )
                                    # Apply the effects
                                    self.diplomatic_consequence.apply_effects(effects, self)
                                break
                
                # Update active effects for the new turn
                self.diplomatic_consequence.update_active_effects(self)
        
        # Check for expired coalition proposals
        if hasattr(self.diplomacy, 'coalition_proposals'):
            expired_proposals = []
            for proposal_id, proposal in self.diplomacy.coalition_proposals.items():
                if proposal['status'] == 'pending' and proposal['proposal_turn'] < self.current_turn - 3:
                    # Proposal expired after 3 turns
                    self.diplomacy.expire_coalition_proposal(proposal_id, self.current_turn)
                    expired_proposals.append({
                        'type': 'proposal_expired',
                        'proposal_id': proposal_id,
                        'coalition_name': proposal.get('coalition_name', 'Unnamed Coalition'),
                        'proposer': proposal['proposing_country']
                    })
            events.extend(expired_proposals)
        
        # Have AI countries evaluate coalition state and make decisions
        ai_decisions = self.decide_coalition_actions()
        
        # Process natural coalition events (random events)
        natural_events = self._process_natural_coalition_events()
        events.extend(natural_events)
        
        return events
        
    def _process_natural_coalition_events(self):
        """
        Process natural coalition events that occur randomly.
        These include internal conflicts, external pressure, and opportunistic actions.
        
        Returns:
            List of events that occurred
        """
        events = []
        
        if not hasattr(self.diplomacy, 'coalitions'):
            return events
            
        for coalition in self.diplomacy.coalitions:
            # Skip inactive coalitions
            if not coalition.is_active(self.current_turn):
                continue
                
            # Calculate probability of internal conflict based on coalition composition
            conflict_chance = 0.1  # Base 10% chance per turn
            
            # Internal conflicts more likely in low-cohesion coalitions
            if coalition.cohesion_level < 0.4:
                conflict_chance += (0.4 - coalition.cohesion_level) * 0.5
                
            # Larger coalitions have more potential for conflict
            if len(coalition.member_countries) > 5:
                conflict_chance += (len(coalition.member_countries) - 5) * 0.02
                
            # Check for internal conflict
            if random.random() < conflict_chance:
                # Select two random members for conflict
                if len(coalition.member_countries) >= 2:
                    conflicting_members = random.sample(list(coalition.member_countries), 2)
                    
                    # Generate conflict reason
                    reasons = ['economic dispute', 'policy disagreement', 'leadership contest', 
                              'resource allocation', 'external relationship disagreement']
                    conflict_reason = random.choice(reasons)
                    
                    # Calculate severity (0.1-1.0)
                    severity = random.uniform(0.1, 1.0)
                    
                    # Apply cohesion penalty
                    cohesion_penalty = -0.05 * severity
                    old_cohesion = coalition.cohesion_level
                    coalition.update_cohesion(cohesion_penalty)
                    
                    # Create event
                    event = {
                        'type': 'internal_conflict',
                        'coalition': coalition.name,
                        'members': conflicting_members,
                        'reason': conflict_reason,
                        'severity': severity,
                        'cohesion_change': cohesion_penalty,
                        'old_cohesion': old_cohesion,
                        'new_cohesion': coalition.cohesion_level
                    }
                    events.append(event)
                    
                    # Calculate diplomatic consequences
                    if self.diplomatic_consequence:
                        effects = self.diplomatic_consequence.calculate_internal_conflict_effects(
                            coalition,
                            conflicting_members,
                            conflict_reason,
                            severity,
                            self
                        )
                        # Apply the effects
                        self.diplomatic_consequence.apply_effects(effects, self)
            
            # Check for external pressure event
            external_pressure_chance = 0.07  # Base 7% chance
            
            # Coalitions with specific purposes more likely to face external pressure
            if coalition.purpose in ['defense', 'counter']:
                external_pressure_chance += 0.08
                
            if random.random() < external_pressure_chance:
                # Select external country applying pressure
                external_countries = [c for c in self.countries.keys() if c not in coalition.member_countries]
                if external_countries:
                    external_country = random.choice(external_countries)
                    
                    # Generate pressure type
                    pressure_types = ['diplomatic protest', 'trade restrictions', 'competing alliance', 
                                    'propaganda campaign', 'diplomatic isolation attempts']
                    pressure_type = random.choice(pressure_types)
                    
                    # Calculate coalition response strength (0.0-1.0) based on cohesion
                    response_strength = coalition.cohesion_level * random.uniform(0.7, 1.3)  # Some randomness
                    response_strength = max(0.0, min(1.0, response_strength))  # Keep in range
                    
                    # Determine outcome
                    if response_strength > 0.6:
                        outcome = 'strengthened'
                        cohesion_effect = 0.05  # Strengthens coalition
                    elif response_strength > 0.3:
                        outcome = 'neutral'
                        cohesion_effect = 0.0  # No effect
                    else:
                        outcome = 'weakened'
                        cohesion_effect = -0.08  # Weakens coalition
                    
                    # Apply cohesion change
                    old_cohesion = coalition.cohesion_level
                    coalition.update_cohesion(cohesion_effect)
                    
                    # Create event
                    event = {
                        'type': 'external_pressure',
                        'coalition': coalition.name,
                        'external_country': external_country,
                        'pressure_type': pressure_type,
                        'response_strength': response_strength,
                        'outcome': outcome,
                        'cohesion_change': cohesion_effect,
                        'old_cohesion': old_cohesion,
                        'new_cohesion': coalition.cohesion_level
                    }
                    events.append(event)
                    
                    # Calculate diplomatic consequences
                    if self.diplomatic_consequence:
                        effects = self.diplomatic_consequence.calculate_external_pressure_effects(
                            coalition,
                            external_country,
                            pressure_type,
                            outcome,
                            self
                        )
                        # Apply the effects
                        self.diplomatic_consequence.apply_effects(effects, self)
        
        return events

    def process_ai_country_decision(self, country_iso, decision_type, decision_details):
        """
        Process and record an AI country decision for explanation and reference.
        
        Args:
            country_iso: ISO code of the country
            decision_type: Type of decision (trade, war, alliance, etc.)
            decision_details: Dictionary with decision details
        """
        # Basic record
        decision_record = {
            'country': country_iso,
            'type': decision_type,
            'details': decision_details,
            'turn': self.current_turn,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Get explanation if ai_explanation_system exists
        if hasattr(self, 'ai_explanation_system') and self.ai_explanation_system:
            try:
                explanation = self.ai_explanation_system.explain_decision(
                    country_iso, 
                    decision_type, 
                    decision_details, 
                    self
                )
                decision_record['explanation'] = explanation
            except Exception as e:
                logger.error(f"Error generating decision explanation: {e}")
                decision_record['explanation'] = "No explanation available"
        else:
            decision_record['explanation'] = "No explanation system available"
        
        self.ai_decisions_history.append(decision_record)
        return decision_record

    # ... existing methods ...