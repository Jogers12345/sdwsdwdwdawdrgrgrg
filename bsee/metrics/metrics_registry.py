"""""
Central registry for all metrics.
"""""

from typing import Callable, Dict, List

# Import all metric modules
from bsee.metrics.entropy_metrics import EntropyMetrics
from bsee.metrics.compression_metrics import CompressionMetrics
from bsee.metrics.pattern_metrics import PatternMetrics
from bsee.metrics.runlength_metrics import RunLengthMetrics
from bsee.metrics.statistical_metrics import StatisticalMetrics
from bsee.metrics.bitwise_metrics import BitwiseMetrics
from bsee.metrics.structure_metrics import StructureMetrics
from bsee.metrics.complexity_metrics import ComplexityMetrics
from bsee.metrics.file_ideality_metrics import FileIdealityMetrics


class MetricsRegistry:
    """Central registry for all metrics."""""

    def __init__(self):
        """Initialize metrics registry."""""
        self.metrics: Dict[str, Callable] = {}
        self.metric_metadata: Dict[str, Dict[str, any]] = {}
        self._load_all_metrics()

    def _load_all_metrics(self) -> None:
        """Load metrics from all metric modules."""""
        # Load entropy metrics
        entropy_metrics = EntropyMetrics()
        for name, func in entropy_metrics.get_metrics().items():
            self.register_metric(name, func, entropy_metrics.get_metadata(name))

        # Load compression metrics
        compression_metrics = CompressionMetrics()
        for name, func in compression_metrics.get_metrics().items():
            self.register_metric(name, func, compression_metrics.get_metadata(name))

        # Load pattern metrics
        pattern_metrics = PatternMetrics()
        for name, func in pattern_metrics.get_metrics().items():
            self.register_metric(name, func, pattern_metrics.get_metadata(name))

        # Load runlength metrics
        runlength_metrics = RunLengthMetrics()
        for name, func in runlength_metrics.get_metrics().items():
            self.register_metric(name, func, runlength_metrics.get_metadata(name))

        # Load statistical metrics
        statistical_metrics = StatisticalMetrics()
        for name, func in statistical_metrics.get_metrics().items():
            self.register_metric(name, func, statistical_metrics.get_metadata(name))

        # Load bitwise metrics
        bitwise_metrics = BitwiseMetrics()
        for name, func in bitwise_metrics.get_metrics().items():
            self.register_metric(name, func, bitwise_metrics.get_metadata(name))

        # Load structure metrics
        structure_metrics = StructureMetrics()
        for name, func in structure_metrics.get_metrics().items():
            self.register_metric(name, func, structure_metrics.get_metadata(name))

        # Load complexity metrics
        complexity_metrics = ComplexityMetrics()
        for name, func in complexity_metrics.get_metrics().items():
            self.register_metric(name, func, complexity_metrics.get_metadata(name))

        # Load file ideality metrics
        ideality_metrics = FileIdealityMetrics()
        for name, func in ideality_metrics.get_metrics().items():
            self.register_metric(name, func, ideality_metrics.get_metadata(name))

    def register_metric(self, name: str, function: Callable, metadata: Dict[str, any]) -> None:
        """Register a metric with the registry."""""
        self.metrics[name] = function
        self.metric_metadata[name] = metadata

    def calculate_metric(self, binary_data: bytes, metric_name: str) -> float:
        """Calculate a single metric."""""
        if metric_name not in self.metrics:
            raise ValueError(f"Unknown metric: {metric_name}")""

        try:
            return self.metrics[metric_name](binary_data)
        except Exception as e:
            # Return 0 or handle error gracefully
            print(f"Warning: Error calculating metric {metric_name}: {e}")""
            return 0.0

    def calculate_metrics(self, binary_data: bytes, metric_names: List[str]) -> Dict[str, float]:
        """Calculate multiple metrics."""""
        results = {}
        for metric_name in metric_names:
            if metric_name in self.metrics:
                try:
                    results[metric_name] = self.metrics[metric_name](binary_data)
                except Exception as e:
                    print(f"Warning: Error calculating metric {metric_name}: {e}")""
                    results[metric_name] = 0.0
            else:
                print(f"Warning: Unknown metric {metric_name}")""
                results[metric_name] = 0.0
        return results

    def calculate_all_metrics(self, binary_data: bytes) -> Dict[str, float]:
        """Calculate all available metrics."""""
        return self.calculate_metrics(binary_data, list(self.metrics.keys()))

    def list_metrics(self) -> List[str]:
        """List all available metric names."""""
        return list(self.metrics.keys())

    def get_metric_metadata(self, metric_name: str) -> Dict[str, any]:
        """Get metadata for a metric."""""
        if metric_name not in self.metric_metadata:
            raise ValueError(f"Unknown metric: {metric_name}")""
        return self.metric_metadata[metric_name]

    def get_metrics_by_category(self, category: str) -> Dict[str, Callable]:
        """Get all metrics in a specific category."""""
        filtered_metrics = {}
        for name, func in self.metrics.items():
            metadata = self.metric_metadata.get(name, {})
            if metadata.get('category') == category:''
                filtered_metrics[name] = func
        return filtered_metrics

    def get_metric_categories(self) -> List[str]:
        """Get all available metric categories."""""
        categories = set()
        for metadata in self.metric_metadata.values():
            category = metadata.get('category')''
            if category:
                categories.add(category)
        return list(categories)

    def get_registry_summary(self) -> Dict[str, any]:
        """Get a summary of the metrics registry."""""
        category_counts = {}
        for metadata in self.metric_metadata.values():
            category = metadata.get('category', 'unknown')''
            category_counts[category] = category_counts.get(category, 0) + 1

        return {
            'total_metrics': len(self.metrics),
            'categories': category_counts,
            'metrics': list(self.metrics.keys())
        }