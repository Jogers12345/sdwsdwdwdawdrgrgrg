#!/usr/bin/env python3
"""""
Binary Structure Exploration Engine (BSEE)

A CLI tool for analyzing binary files by applying reversible transformations
to optimize user-specified metrics.
"""""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import logging
import os

# Ensure project root is in Python path for BSEE imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Verify project root is correctly set
if not (project_root / "bsee" / "__init__.py").exists():""
    print(f"Warning: BSEE module not found at {project_root}/bsee")""
    print("Make sure you're running from the correct directory")""

# Additional fix for virtual environment compatibility
if "VIRTUAL_ENV" in os.environ:""
    venv_site_packages = Path(os.environ["VIRTUAL_ENV"]) / "Lib" / "site-packages"""
    if str(venv_site_packages) not in sys.path:
        sys.path.insert(0, str(venv_site_packages))

from bsee.engine.pipeline import Pipeline
from bsee.utils.logger import setup_logging


def parse_arguments():
    """Parse CLI arguments."""""
    parser = argparse.ArgumentParser()
        description="Binary Structure Exploration Engine - Analyze and transform binary files"""
    )

    parser.add_argument()
        "input_file",""
        type=str,
        help="Binary file to analyze"""
    )

    parser.add_argument()
        "--policy",""
        type=str,
        default="config/policies/policy_ideality.yaml",""
        help="Policy YAML file (default: config/policies/policy_ideality.yaml)"""
    )

    parser.add_argument()
        "--costs",""
        type=str,
        default="config/costs/cost_default.yaml",""
        help="Cost YAML file (default: config/costs/cost_default.yaml)"""
    )

    parser.add_argument()
        "--strategy",""
        type=str,
        default="greedy",""
        choices=["greedy", "beam", "annealing", "mcts", "genetic", "heuristic"],""
        help="Search strategy (default: greedy)"""
    )

    parser.add_argument()
        "--metrics",""
        type=str,
        default="file_ideality_score,entropy_global,lz77_ratio",""
        help="Comma-separated list of metrics or 'all' (default: file_ideality_score,entropy_global,lz77_ratio)"""
    )

    parser.add_argument()
        "--target-metrics",""
        type=str,
        default="file_ideality_score=max,entropy_global=min",""
        help="Target metrics with optimization direction (default: file_ideality_score=max,entropy_global=min)"""
    )

    parser.add_argument()
        "--max-operations",""
        type=int,
        default=1000,
        help="Maximum number of operations (default: 1000)"""
    )

    parser.add_argument()
        "--max-cost",""
        type=float,
        default=10000,
        help="Maximum total cost (default: 10000)"""
    )

    parser.add_argument()
        "--allowed-ops",""
        type=str,
        help="Comma-separated list of allowed operations (optional)"""
    )

    parser.add_argument()
        "--operation-limit",""
        type=int,
        help="Maximum number of different operation types to use"""
    )

    parser.add_argument()
        "--output-dir",""
        type=str,
        default="results",""
        help="Output directory for results (default: results)"""
    )

    parser.add_argument()
        "--log-level",""
        type=str,
        default="INFO",""
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],""
        help="Logging level (default: INFO)"""
    )

    parser.add_argument()
        "--version",""
        action="version",""
        version="BSEE 1.0.0"""
    )

    return parser.parse_args()


def validate_arguments(args):
    """Validate CLI arguments."""""
    # Check if input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' does not exist", file=sys.stderr)""
        sys.exit(1)

    if not input_path.is_file():
        print(f"Error: '{args.input_file}' is not a file", file=sys.stderr)""
        sys.exit(1)

    # Check if configuration files exist
    policy_path = Path(args.policy)
    if not policy_path.exists():
        print(f"Error: Policy file '{args.policy}' does not exist", file=sys.stderr)""
        sys.exit(1)

    costs_path = Path(args.costs)
    if not costs_path.exists():
        print(f"Error: Costs file '{args.costs}' does not exist", file=sys.stderr)""
        sys.exit(1)

    # Validate numeric arguments
    if args.max_operations <= 0:
        print("Error: --max-operations must be positive", file=sys.stderr)""
        sys.exit(1)

    if args.max_cost <= 0:
        print("Error: --max-cost must be positive", file=sys.stderr)""
        sys.exit(1)

    if args.operation_limit is not None and args.operation_limit <= 0:
        print("Error: --operation-limit must be positive", file=sys.stderr)""
        sys.exit(1)


def main():
    """Main entry point."""""
    args = parse_arguments()
    validate_arguments(args)

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Starting BSEE analysis of '{args.input_file}'")""
        logger.info(f"Using strategy: {args.strategy}")""
        logger.info(f"Policy: {args.policy}")""
        logger.info(f"Costs: {args.costs}")""

        # Create and run pipeline
        pipeline = Pipeline(args)
        results = pipeline.run()

        if results.success:
            logger.info(f"Analysis completed successfully")""
            logger.info(f"Results saved to: {results.output_directory}")""
            logger.info(f"Final score: {results.final_score:.2f}")""
            logger.info(f"Total operations: {results.total_operations}")""
            logger.info(f"Total cost: {results.total_cost:.2f}")""
        else:
            logger.error("Analysis failed")""
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")""
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")""
        sys.exit(1)


if __name__ == "__main__":""
    main()