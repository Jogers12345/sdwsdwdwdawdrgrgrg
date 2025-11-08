"""
Transformation Export Capabilities for BSEE

Provides comprehensive export functionality for transformation sequences,
visualizations, and analysis results in multiple formats.
"""

import os
import json
import csv
import base64
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Tuple, Optional, Any, BinaryIO
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
import threading

# Check for available export libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import imageio
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False


@dataclass
class ExportConfig:
    """Configuration for export operations."""
    format_type: str = "png"  # png, svg, pdf, json, csv, xml, html, markdown
    quality: int = 95  # For lossy formats
    dpi: int = 150  # Resolution for images
    include_metadata: bool = True
    include_timestamps: bool = True
    include_byte_analysis: bool = True
    animation_fps: int = 10  # For animated exports
    animation_duration: float = 5.0  # seconds
    compression_level: int = 6  # For compressed formats


class TransformationExporter:
    """Handles export of transformation sequences and visualizations."""

    def __init__(self, parent_widget=None):
        """
        Initialize transformation exporter.

        Args:
            parent_widget: Parent widget for dialogs
        """
        self.parent_widget = parent_widget
        self.config = ExportConfig()
        self.export_queue = []
        self.is_exporting = False

        # Check available formats
        self.available_formats = self._check_available_formats()

        # Initialize export progress window
        self.progress_window = None
        self.progress_var = None
        self.status_var = None

    def _check_available_formats(self) -> Dict[str, List[str]]:
        """Check which export formats are available."""
        formats = {
            'video': [],
            'image': [],
            'report': [],
            'data': []
        }

        # Video formats
        if IMAGEIO_AVAILABLE:
            formats['video'].extend(['mp4', 'webm', 'gif', 'avi'])
        if MATPLOTLIB_AVAILABLE:
            formats['video'].extend(['animated_gif'])

        # Image formats
        formats['image'].extend(['png', 'svg', 'pdf'])
        if PIL_AVAILABLE:
            formats['image'].extend(['jpg', 'jpeg', 'bmp', 'tiff'])

        # Report formats
        formats['report'].extend(['html', 'pdf', 'markdown', 'txt'])

        # Data formats
        formats['data'].extend(['json', 'csv', 'xml', 'yaml'])

        return formats

    def export_transformation_sequence(self, transformation_data: Dict[str, Any],
                                     filename: str = None, config: ExportConfig = None) -> bool:
        """
        Export complete transformation sequence.

        Args:
            transformation_data: Dictionary containing transformation sequence data
            filename: Output filename (optional, will prompt if not provided)
            config: Export configuration (optional)

        Returns:
            True if export successful, False otherwise
        """
        if config:
            self.config = config

        if not filename:
            filename = self._get_save_filename()

        if not filename:
            return False

        try:
            file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
            self.config.format_type = file_ext

            if file_ext in self.available_formats['video']:
                return self._export_video(transformation_data, filename)
            elif file_ext in self.available_formats['image']:
                return self._export_image(transformation_data, filename)
            elif file_ext in self.available_formats['report']:
                return self._export_report(transformation_data, filename)
            elif file_ext in self.available_formats['data']:
                return self._export_data(transformation_data, filename)
            else:
                messagebox.showerror("Export Error", f"Unsupported format: {file_ext}")
                return False

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")
            return False

    def export_visualization_frames(self, transformation_data: Dict[str, Any],
                                   output_dir: str = None, config: ExportConfig = None) -> bool:
        """
        Export individual frames from transformation visualization.

        Args:
            transformation_data: Dictionary containing transformation sequence data
            output_dir: Output directory for frames
            config: Export configuration

        Returns:
            True if export successful, False otherwise
        """
        if config:
            self.config = config

        if not output_dir:
            output_dir = filedialog.askdirectory(title="Select Output Directory for Frames")
            if not output_dir:
                return False

        try:
            operations = transformation_data.get('operations', [])
            total_frames = len(operations)

            # Create progress window
            self._create_progress_window(f"Exporting {total_frames} frames...")

            for i, operation in enumerate(operations):
                frame_filename = os.path.join(output_dir, f"frame_{i:04d}.png")
                self._export_operation_frame(operation, frame_filename, i, total_frames)

                # Update progress
                if self.progress_var:
                    progress = (i + 1) / total_frames * 100
                    self.progress_var.set(progress)
                    self.parent_widget.update()

            self._close_progress_window()
            messagebox.showinfo("Export Complete", f"Exported {total_frames} frames to {output_dir}")
            return True

        except Exception as e:
            self._close_progress_window()
            messagebox.showerror("Export Error", f"Failed to export frames: {e}")
            return False

    def _export_video(self, transformation_data: Dict[str, Any], filename: str) -> bool:
        """Export transformation as video (MP4, WebM, GIF, AVI)."""
        if not IMAGEIO_AVAILABLE and not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Export Error", "Video export requires imageio or matplotlib")
            return False

        operations = transformation_data.get('operations', [])
        if not operations:
            messagebox.showwarning("No Data", "No operations to export")
            return False

        # Create progress window
        self._create_progress_window(f"Creating video from {len(operations)} frames...")

        # Generate frames
        frames = []
        temp_files = []

        try:
            for i, operation in enumerate(operations):
                # Create frame
                frame_data = self._create_frame_from_operation(operation, i)
                frames.append(frame_data)

                # Update progress
                progress = (i + 1) / len(operations) * 50  # First 50% for frame creation
                if self.progress_var:
                    self.progress_var.set(progress)
                    self.parent_widget.update()

            # Save video
            if IMAGEIO_AVAILABLE:
                self._save_video_with_imageio(frames, filename)
            else:
                self._save_animated_gif_with_matplotlib(frames, filename)

            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass

            self._close_progress_window()
            messagebox.showinfo("Export Complete", f"Video exported to {filename}")
            return True

        except Exception as e:
            self._close_progress_window()
            raise e

    def _export_image(self, transformation_data: Dict[str, Any], filename: str) -> bool:
        """Export transformation as static image (PNG, SVG, PDF, JPG)."""
        operations = transformation_data.get('operations', [])
        if not operations:
            messagebox.showwarning("No Data", "No operations to export")
            return False

        try:
            # Export summary image showing before/after states
            self._create_summary_image(transformation_data, filename)
            messagebox.showinfo("Export Complete", f"Image exported to {filename}")
            return True

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export image: {e}")
            return False

    def _export_report(self, transformation_data: Dict[str, Any], filename: str) -> bool:
        """Export transformation as detailed report (HTML, PDF, Markdown, TXT)."""
        try:
            file_ext = os.path.splitext(filename)[1].lower().lstrip('.')

            if file_ext == 'html':
                self._export_html_report(transformation_data, filename)
            elif file_ext == 'pdf':
                self._export_pdf_report(transformation_data, filename)
            elif file_ext in ['markdown', 'md']:
                self._export_markdown_report(transformation_data, filename)
            elif file_ext == 'txt':
                self._export_text_report(transformation_data, filename)
            else:
                raise ValueError(f"Unsupported report format: {file_ext}")

            messagebox.showinfo("Export Complete", f"Report exported to {filename}")
            return True

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {e}")
            return False

    def _export_data(self, transformation_data: Dict[str, Any], filename: str) -> bool:
        """Export transformation as structured data (JSON, CSV, XML, YAML)."""
        try:
            file_ext = os.path.splitext(filename)[1].lower().lstrip('.')

            if file_ext == 'json':
                self._export_json_data(transformation_data, filename)
            elif file_ext == 'csv':
                self._export_csv_data(transformation_data, filename)
            elif file_ext == 'xml':
                self._export_xml_data(transformation_data, filename)
            elif file_ext in ['yaml', 'yml']:
                self._export_yaml_data(transformation_data, filename)
            else:
                raise ValueError(f"Unsupported data format: {file_ext}")

            messagebox.showinfo("Export Complete", f"Data exported to {filename}")
            return True

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
            return False

    def _create_frame_from_operation(self, operation: Dict[str, Any], frame_index: int) -> Any:
        """Create visualization frame from operation data."""
        if not MATPLOTLIB_AVAILABLE:
            # Fallback to PIL-based frame creation
            return self._create_pil_frame(operation, frame_index)

        # Create matplotlib figure
        fig = plt.figure(figsize=(12, 8), dpi=self.config.dpi)
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 3], width_ratios=[1, 1])

        # Title and info
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        title_text = f"Step {frame_index + 1}: {operation.get('name', 'Unknown Operation')}"
        ax_title.text(0.5, 0.5, title_text, ha='center', va='center', fontsize=14, fontweight='bold')

        # Before data
        ax_before = fig.add_subplot(gs[1, 0])
        self._plot_hex_visualization(ax_before, operation.get('before_hex', ''), "Before")

        # After data
        ax_after = fig.add_subplot(gs[1, 1])
        self._plot_hex_visualization(ax_after, operation.get('after_hex', ''), "After")

        plt.tight_layout()

        # Convert to image
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        image = np.frombuffer(canvas.tostring_rgb(), dtype=np.uint8)
        image = image.reshape(canvas.get_width_height()[::-1] + (3,))

        plt.close(fig)
        return image

    def _create_pil_frame(self, operation: Dict[str, Any], frame_index: int) -> Any:
        """Create PIL-based frame (fallback method)."""
        if not PIL_AVAILABLE:
            raise ImportError("PIL is required for frame creation")

        # Create image
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='#1e1e1e')
        draw = ImageDraw.Draw(image)

        # Draw title
        title = f"Step {frame_index + 1}: {operation.get('name', 'Unknown Operation')}"
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()

        draw.text((10, 10), title, fill='#00ff00', font=font)

        # Draw simple hex visualization
        self._draw_simple_hex_visualization(draw, operation.get('before_hex', ''), 10, 50, 380, 500)
        self._draw_simple_hex_visualization(draw, operation.get('after_hex', ''), 410, 50, 380, 500)

        return image

    def _plot_hex_visualization(self, ax, hex_data: str, title: str):
        """Plot hex visualization in matplotlib axis."""
        ax.clear()
        ax.set_title(title, fontsize=12, fontweight='bold')

        if not hex_data:
            ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
            return

        try:
            # Convert hex to bytes
            data = bytes.fromhex(hex_data)
            data_len = len(data)

            # Create heatmap visualization
            if data_len > 0:
                # Reshape data for visualization
                grid_size = int(np.ceil(np.sqrt(data_len)))
                grid_data = np.zeros((grid_size, grid_size), dtype=np.uint8)

                for i, byte_val in enumerate(data):
                    row = i // grid_size
                    col = i % grid_size
                    grid_data[row, col] = byte_val

                # Display as heatmap
                im = ax.imshow(grid_data, cmap='viridis', aspect='auto')
                ax.set_xlabel("Column")
                ax.set_ylabel("Row")

                # Add colorbar
                plt.colorbar(im, ax=ax, label="Byte Value")

        except Exception as e:
            ax.text(0.5, 0.5, f"Error: {e}", ha='center', va='center', transform=ax.transAxes)

    def _draw_simple_hex_visualization(self, draw, hex_data: str, x: int, y: int, width: int, height: int):
        """Draw simple hex visualization with PIL."""
        if not hex_data:
            return

        try:
            data = bytes.fromhex(hex_data)
            data_len = min(len(data), 256)  # Limit to first 256 bytes

            # Draw hex bytes
            bytes_per_line = 16
            for i in range(0, data_len, bytes_per_line):
                line_y = y + (i // bytes_per_line) * 15

                # Address
                addr_text = f"{i:04x}:"
                draw.text((x, line_y), addr_text, fill='#808080')

                # Hex bytes
                hex_text = ""
                for j in range(bytes_per_line):
                    if i + j < data_len:
                        byte_val = data[i + j]
                        hex_text += f"{byte_val:02x} "
                    else:
                        hex_text += "   "

                draw.text((x + 50, line_y), hex_text, fill='#00ff00')

        except Exception as e:
            draw.text((x, y + height//2), f"Error: {e}", fill='#ff0000')

    def _save_video_with_imageio(self, frames: List[Any], filename: str):
        """Save video using imageio."""
        file_ext = os.path.splitext(filename)[1].lower().lstrip('.')

        if file_ext == 'gif':
            imageio.mimsave(filename, frames, fps=self.config.animation_fps)
        elif file_ext in ['mp4', 'avi']:
            # Convert frames to proper format if needed
            writer = imageio.get_writer(filename, fps=self.config.animation_fps)
            for frame in frames:
                writer.append_data(frame)
            writer.close()
        elif file_ext == 'webm':
            imageio.mimsave(filename, frames, fps=self.config.animation_fps, format='webm')

    def _save_animated_gif_with_matplotlib(self, frames: List[Any], filename: str):
        """Save animated GIF using matplotlib."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required for GIF export")

        fig, ax = plt.subplots(figsize=(10, 6))

        def animate(frame_num):
            ax.clear()
            if frame_num < len(frames):
                ax.imshow(frames[frame_num])
                ax.set_title(f"Frame {frame_num + 1}")
            ax.axis('off')

        anim = FuncAnimation(fig, animate, frames=len(frames), interval=1000/self.config.animation_fps)
        anim.save(filename, writer='pillow', fps=self.config.animation_fps)
        plt.close(fig)

    def _create_summary_image(self, transformation_data: Dict[str, Any], filename: str):
        """Create summary image showing before/after states."""
        operations = transformation_data.get('operations', [])
        if not operations:
            return

        if not MATPLOTLIB_AVAILABLE:
            self._create_pil_summary_image(transformation_data, filename)
            return

        # Create comprehensive summary figure
        fig = plt.figure(figsize=(16, 12), dpi=self.config.dpi)

        # Create grid layout
        gs = fig.add_gridspec(3, 3, height_ratios=[1, 3, 2], width_ratios=[1, 1, 1])

        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        title = "BSEE Transformation Analysis Summary"
        if self.config.include_timestamps:
            title += f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ax_title.text(0.5, 0.5, title, ha='center', va='center', fontsize=16, fontweight='bold')

        # Original data
        ax_original = fig.add_subplot(gs[1, 0])
        if operations:
            self._plot_hex_visualization(ax_original, operations[0].get('before_hex', ''), "Original Data")

        # Final data
        ax_final = fig.add_subplot(gs[1, 1])
        if operations:
            self._plot_hex_visualization(ax_final, operations[-1].get('after_hex', ''), "Final Data")

        # Statistics
        ax_stats = fig.add_subplot(gs[1, 2])
        self._plot_transformation_statistics(ax_stats, transformation_data)

        # Metrics evolution
        ax_metrics = fig.add_subplot(gs[2, :])
        self._plot_metrics_evolution(ax_metrics, transformation_data)

        plt.tight_layout()

        # Save based on format
        file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
        if file_ext in ['png', 'jpg', 'jpeg', 'bmp', 'tiff']:
            fig.savefig(filename, dpi=self.config.dpi, bbox_inches='tight')
        elif file_ext == 'svg':
            fig.savefig(filename, format='svg', bbox_inches='tight')
        elif file_ext == 'pdf':
            fig.savefig(filename, format='pdf', bbox_inches='tight')

        plt.close(fig)

    def _create_pil_summary_image(self, transformation_data: Dict[str, Any], filename: str):
        """Create PIL-based summary image (fallback)."""
        if not PIL_AVAILABLE:
            raise ImportError("PIL is required for image export")

        width, height = 1200, 800
        image = Image.new('RGB', (width, height), color='#1e1e1e')
        draw = ImageDraw.Draw(image)

        try:
            font_title = ImageFont.truetype("arial.ttf", 20)
            font_text = ImageFont.truetype("arial.ttf", 12)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()

        # Title
        title = "BSEE Transformation Analysis Summary"
        draw.text((50, 30), title, fill='#00ff00', font=font_title)

        # Basic statistics
        operations = transformation_data.get('operations', [])
        if operations:
            stats_text = f"Total Operations: {len(operations)}"
            draw.text((50, 80), stats_text, fill='#00ff00', font=font_text)

            # Before/after comparison
            before_hex = operations[0].get('before_hex', '')
            after_hex = operations[-1].get('after_hex', '')

            draw.text((50, 120), "Before:", fill='#00ff00', font=font_text)
            self._draw_simple_hex_visualization(draw, before_hex, 50, 150, 500, 300)

            draw.text((600, 120), "After:", fill='#00ff00', font=font_text)
            self._draw_simple_hex_visualization(draw, after_hex, 600, 150, 500, 300)

        image.save(filename, quality=self.config.quality)

    def _plot_transformation_statistics(self, ax, transformation_data: Dict[str, Any]):
        """Plot transformation statistics."""
        ax.clear()
        ax.set_title("Transformation Statistics", fontsize=12, fontweight='bold')

        operations = transformation_data.get('operations', [])
        if not operations:
            ax.text(0.5, 0.5, "No operations", ha='center', va='center', transform=ax.transAxes)
            return

        # Calculate statistics
        operation_types = {}
        total_changes = 0
        total_time = 0

        for op in operations:
            op_type = op.get('name', 'Unknown')
            operation_types[op_type] = operation_types.get(op_type, 0) + 1

            changes = len(op.get('byte_changes', []))
            total_changes += changes

            timing = op.get('timing', {}).get('execution_time', 0)
            total_time += timing

        # Create pie chart of operation types
        if operation_types:
            labels = list(operation_types.keys())
            sizes = list(operation_types.values())
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')

        # Add text statistics
        stats_text = f"Total Changes: {total_changes}\n"
        stats_text += f"Total Time: {total_time:.4f}s\n"
        stats_text += f"Avg Time/Op: {total_time/len(operations):.4f}s"

        ax.text(1.2, 0.5, stats_text, transform=ax.transAxes, fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))

    def _plot_metrics_evolution(self, ax, transformation_data: Dict[str, Any]):
        """Plot metrics evolution over transformations."""
        ax.clear()
        ax.set_title("Metrics Evolution", fontsize=12, fontweight='bold')

        operations = transformation_data.get('operations', [])
        if not operations:
            ax.text(0.5, 0.5, "No metrics data", ha='center', va='center', transform=ax.transAxes)
            return

        # Extract metrics data
        steps = list(range(len(operations)))
        entropy_values = []
        compression_ratios = []

        for i, op in enumerate(operations):
            metrics_before = op.get('metrics_before', {})
            metrics_after = op.get('metrics_after', {})

            # Use entropy if available
            entropy = metrics_after.get('shannon_entropy', metrics_before.get('shannon_entropy', 0))
            entropy_values.append(entropy)

            # Calculate compression ratio if possible
            before_size = len(bytes.fromhex(op.get('before_hex', '')))
            after_size = len(bytes.fromhex(op.get('after_hex', '')))
            if before_size > 0:
                ratio = after_size / before_size
                compression_ratios.append(ratio)

        # Plot entropy
        ax2 = ax.twinx()
        line1 = ax.plot(steps, entropy_values, 'b-', label='Entropy', linewidth=2)
        ax.set_xlabel('Operation Step')
        ax.set_ylabel('Entropy', color='b')
        ax.tick_params(axis='y', labelcolor='b')

        # Plot compression ratio
        if compression_ratios:
            line2 = ax2.plot(steps, compression_ratios, 'r-', label='Compression Ratio', linewidth=2)
            ax2.set_ylabel('Compression Ratio', color='r')
            ax2.tick_params(axis='y', labelcolor='r')

        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')

    def _export_html_report(self, transformation_data: Dict[str, Any], filename: str):
        """Export transformation as HTML report."""
        html_content = self._generate_html_report(transformation_data)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _generate_html_report(self, transformation_data: Dict[str, Any]) -> str:
        """Generate HTML report content."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>BSEE Transformation Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .header { background-color: #333; color: white; padding: 20px; border-radius: 5px; }
        .section { background-color: white; margin: 20px 0; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .hex-display { font-family: monospace; background-color: #1e1e1e; color: #00ff00; padding: 10px; border-radius: 3px; }
        .metrics-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        .metrics-table th, .metrics-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .metrics-table th { background-color: #f2f2f2; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .stat-card { background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }
    </style>
</head>
<body>
"""

        # Header
        html += """<div class="header">
    <h1>BSEE Transformation Analysis Report</h1>
"""
        if self.config.include_timestamps:
            html += f"<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        html += "</div>"

        # Summary section
        html += self._generate_html_summary(transformation_data)

        # Operations section
        html += self._generate_html_operations(transformation_data)

        # Metrics section
        html += self._generate_html_metrics(transformation_data)

        html += "</body></html>"
        return html

    def _generate_html_summary(self, transformation_data: Dict[str, Any]) -> str:
        """Generate HTML summary section."""
        operations = transformation_data.get('operations', [])

        html = """<div class="section">
    <h2>Summary</h2>
    <div class="stats-grid">
"""

        # Calculate statistics
        total_operations = len(operations)
        total_changes = sum(len(op.get('byte_changes', [])) for op in operations)
        total_time = sum(op.get('timing', {}).get('execution_time', 0) for op in operations)

        html += f"""
        <div class="stat-card">
            <h3>{total_operations}</h3>
            <p>Total Operations</p>
        </div>
        <div class="stat-card">
            <h3>{total_changes}</h3>
            <p>Total Byte Changes</p>
        </div>
        <div class="stat-card">
            <h3>{total_time:.4f}s</h3>
            <p>Total Execution Time</p>
        </div>
"""

        html += "    </div>\n</div>\n"
        return html

    def _generate_html_operations(self, transformation_data: Dict[str, Any]) -> str:
        """Generate HTML operations section."""
        operations = transformation_data.get('operations', [])

        html = """<div class="section">
    <h2>Operations</h2>
"""

        for i, op in enumerate(operations):
            html += f"""    <h3>Step {i+1}: {op.get('name', 'Unknown')}</h3>
    <p><strong>Parameters:</strong> {op.get('params', {})}</p>
    <p><strong>Execution Time:</strong> {op.get('timing', {}).get('execution_time', 0):.4f}s</p>
    <p><strong>Bytes Changed:</strong> {len(op.get('byte_changes', []))}</p>
"""

            if self.config.include_byte_analysis:
                html += """    <div class="hex-display">
        <strong>Before:</strong><br>
"""
                before_hex = op.get('before_hex', '')
                if before_hex:
                    # Format hex for display
                    formatted_hex = self._format_hex_for_html(before_hex)
                    html += f"        <pre>{formatted_hex}</pre>"

                html += """        <strong>After:</strong><br>
"""
                after_hex = op.get('after_hex', '')
                if after_hex:
                    formatted_hex = self._format_hex_for_html(after_hex)
                    html += f"        <pre>{formatted_hex}</pre>"

                html += "    </div>\n"

        html += "</div>\n"
        return html

    def _format_hex_for_html(self, hex_data: str) -> str:
        """Format hex data for HTML display."""
        if not hex_data:
            return "No data"

        try:
            data = bytes.fromhex(hex_data)
            lines = []

            for i in range(0, len(data), 16):
                addr = f"{i:08x}: "
                hex_bytes = []
                ascii_text = ""

                for j in range(16):
                    if i + j < len(data):
                        byte_val = data[i + j]
                        hex_bytes.append(f"{byte_val:02x}")
                        if 32 <= byte_val <= 126:
                            ascii_text += chr(byte_val)
                        else:
                            ascii_text += "."
                    else:
                        hex_bytes.append("  ")
                        ascii_text += " "

                    if j == 7:
                        hex_bytes.append(" ")

                line = addr + " ".join(hex_bytes) + "  " + ascii_text
                lines.append(line)

            return "\n".join(lines)

        except Exception:
            return "Error formatting hex data"

    def _generate_html_metrics(self, transformation_data: Dict[str, Any]) -> str:
        """Generate HTML metrics section."""
        operations = transformation_data.get('operations', [])

        html = """<div class="section">
    <h2>Metrics Evolution</h2>
    <table class="metrics-table">
        <tr>
            <th>Step</th>
            <th>Operation</th>
            <th>Entropy</th>
            <th>Size (bytes)</th>
            <th>Changes</th>
            <th>Time (s)</th>
        </tr>
"""

        for i, op in enumerate(operations):
            metrics_before = op.get('metrics_before', {})
            metrics_after = op.get('metrics_after', {})

            entropy = metrics_after.get('shannon_entropy', metrics_before.get('shannon_entropy', 0))
            size = len(bytes.fromhex(op.get('after_hex', '')))
            changes = len(op.get('byte_changes', []))
            time = op.get('timing', {}).get('execution_time', 0)

            html += f"""        <tr>
            <td>{i+1}</td>
            <td>{op.get('name', 'Unknown')}</td>
            <td>{entropy:.4f}</td>
            <td>{size}</td>
            <td>{changes}</td>
            <td>{time:.4f}</td>
        </tr>
"""

        html += "    </table>\n</div>\n"
        return html

    def _export_pdf_report(self, transformation_data: Dict[str, Any], filename: str):
        """Export transformation as PDF report."""
        # Generate HTML first, then convert to PDF
        html_content = self._generate_html_report(transformation_data)
        temp_html = filename.replace('.pdf', '_temp.html')

        try:
            # Save temporary HTML
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Convert to PDF using weasyprint if available
            try:
                import weasyprint
                weasyprint.HTML(string=html_content).write_pdf(filename)
            except ImportError:
                # Fallback: use headless Chrome if available
                try:
                    subprocess.run([
                        'google-chrome', '--headless', '--disable-gpu',
                        '--print-to-pdf=' + filename, temp_html
                    ], check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # Final fallback: save as text file with .pdf extension
                    messagebox.showwarning("PDF Export Limited",
                                        "PDF export libraries not available. Exporting as text file.")
                    self._export_text_report(transformation_data, filename.replace('.pdf', '.txt'))
                    return

            # Clean up temporary file
            try:
                os.remove(temp_html)
            except:
                pass

        except Exception as e:
            # Clean up on error
            try:
                if os.path.exists(temp_html):
                    os.remove(temp_html)
            except:
                pass
            raise e

    def _export_markdown_report(self, transformation_data: Dict[str, Any], filename: str):
        """Export transformation as Markdown report."""
        operations = transformation_data.get('operations', [])

        markdown = f"""# BSEE Transformation Analysis Report

"""
        if self.config.include_timestamps:
            markdown += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Summary
        total_operations = len(operations)
        total_changes = sum(len(op.get('byte_changes', [])) for op in operations)
        total_time = sum(op.get('timing', {}).get('execution_time', 0) for op in operations)

        markdown += f"""## Summary

- **Total Operations:** {total_operations}
- **Total Byte Changes:** {total_changes}
- **Total Execution Time:** {total_time:.4f}s

## Operations

"""

        for i, op in enumerate(operations):
            markdown += f"""### Step {i+1}: {op.get('name', 'Unknown')}

**Parameters:** {op.get('params', {})}
**Execution Time:** {op.get('timing', {}).get('execution_time', 0):.4f}s
**Bytes Changed:** {len(op.get('byte_changes', []))}

"""

            if self.config.include_byte_analysis:
                before_hex = op.get('before_hex', '')
                after_hex = op.get('after_hex', '')

                if before_hex:
                    markdown += f"**Before:**\n```\n{self._format_hex_for_markdown(before_hex)}\n```\n\n"

                if after_hex:
                    markdown += f"**After:**\n```\n{self._format_hex_for_markdown(after_hex)}\n```\n\n"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown)

    def _format_hex_for_markdown(self, hex_data: str) -> str:
        """Format hex data for Markdown display."""
        return self._format_hex_for_html(hex_data)

    def _export_text_report(self, transformation_data: Dict[str, Any], filename: str):
        """Export transformation as plain text report."""
        operations = transformation_data.get('operations', [])

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("BSEE Transformation Analysis Report\n")
            f.write("=" * 50 + "\n\n")

            if self.config.include_timestamps:
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Summary
            total_operations = len(operations)
            total_changes = sum(len(op.get('byte_changes', [])) for op in operations)
            total_time = sum(op.get('timing', {}).get('execution_time', 0) for op in operations)

            f.write(f"SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Operations: {total_operations}\n")
            f.write(f"Total Byte Changes: {total_changes}\n")
            f.write(f"Total Execution Time: {total_time:.4f}s\n\n")

            # Operations
            f.write("OPERATIONS\n")
            f.write("-" * 20 + "\n")

            for i, op in enumerate(operations):
                f.write(f"\nStep {i+1}: {op.get('name', 'Unknown')}\n")
                f.write(f"Parameters: {op.get('params', {})}\n")
                f.write(f"Execution Time: {op.get('timing', {}).get('execution_time', 0):.4f}s\n")
                f.write(f"Bytes Changed: {len(op.get('byte_changes', []))}\n")

                if self.config.include_byte_analysis:
                    before_hex = op.get('before_hex', '')
                    after_hex = op.get('after_hex', '')

                    if before_hex:
                        f.write(f"\nBefore:\n")
                        formatted_hex = self._format_hex_for_text(before_hex)
                        f.write(formatted_hex + "\n")

                    if after_hex:
                        f.write(f"\nAfter:\n")
                        formatted_hex = self._format_hex_for_text(after_hex)
                        f.write(formatted_hex + "\n")

    def _format_hex_for_text(self, hex_data: str) -> str:
        """Format hex data for text display."""
        return self._format_hex_for_html(hex_data)

    def _export_json_data(self, transformation_data: Dict[str, Any], filename: str):
        """Export transformation as JSON data."""
        export_data = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat() if self.config.include_timestamps else None,
                'export_config': asdict(self.config),
                'version': '1.0'
            },
            'transformation': transformation_data
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)

    def _export_csv_data(self, transformation_data: Dict[str, Any], filename: str):
        """Export transformation as CSV data."""
        operations = transformation_data.get('operations', [])

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            header = ['Step', 'Operation', 'Parameters', 'Execution Time', 'Bytes Changed',
                     'Before Size', 'After Size', 'Entropy Before', 'Entropy After']
            writer.writerow(header)

            # Write data
            for i, op in enumerate(operations):
                metrics_before = op.get('metrics_before', {})
                metrics_after = op.get('metrics_after', {})

                row = [
                    i + 1,
                    op.get('name', 'Unknown'),
                    str(op.get('params', {})),
                    op.get('timing', {}).get('execution_time', 0),
                    len(op.get('byte_changes', [])),
                    len(bytes.fromhex(op.get('before_hex', ''))),
                    len(bytes.fromhex(op.get('after_hex', ''))),
                    metrics_before.get('shannon_entropy', 0),
                    metrics_after.get('shannon_entropy', 0)
                ]
                writer.writerow(row)

    def _export_xml_data(self, transformation_data: Dict[str, Any], filename: str):
        """Export transformation as XML data."""
        xml_content = self._generate_xml(transformation_data)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_content)

    def _generate_xml(self, transformation_data: Dict[str, Any]) -> str:
        """Generate XML content."""
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<transformation_analysis>\n'

        # Metadata
        xml += '  <metadata>\n'
        if self.config.include_timestamps:
            xml += f'    <export_timestamp>{datetime.now().isoformat()}</export_timestamp>\n'
        xml += f'    <version>1.0</version>\n'
        xml += '  </metadata>\n'

        # Operations
        operations = transformation_data.get('operations', [])
        xml += '  <operations>\n'

        for i, op in enumerate(operations):
            xml += f'    <operation step="{i+1}">\n'
            xml += f'      <name>{op.get("name", "Unknown")}</name>\n'
            xml += f'      <parameters>{op.get("params", {})}</parameters>\n'
            xml += f'      <execution_time>{op.get("timing", {}).get("execution_time", 0)}</execution_time>\n'
            xml += f'      <bytes_changed>{len(op.get("byte_changes", []))}</bytes_changed>\n'
            xml += f'      <before_hex>{op.get("before_hex", "")}</before_hex>\n'
            xml += f'      <after_hex>{op.get("after_hex", "")}</after_hex>\n'
            xml += '    </operation>\n'

        xml += '  </operations>\n'
        xml += '</transformation_analysis>\n'

        return xml

    def _export_yaml_data(self, transformation_data: Dict[str, Any], filename: str):
        """Export transformation as YAML data."""
        try:
            import yaml
        except ImportError:
            messagebox.showerror("Export Error", "PyYAML is required for YAML export")
            return

        export_data = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat() if self.config.include_timestamps else None,
                'export_config': asdict(self.config),
                'version': '1.0'
            },
            'transformation': transformation_data
        }

        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(export_data, f, default_flow_style=False)

    def _get_save_filename(self) -> Optional[str]:
        """Get filename from user via save dialog."""
        file_types = []

        # Add available formats
        if self.available_formats['video']:
            video_types = [f"Video files (*.{ext})" for ext in self.available_formats['video']]
            file_types.extend(video_types)

        if self.available_formats['image']:
            image_types = [f"Image files (*.{ext})" for ext in self.available_formats['image']]
            file_types.extend(image_types)

        if self.available_formats['report']:
            report_types = [f"Report files (*.{ext})" for ext in self.available_formats['report']]
            file_types.extend(report_types)

        if self.available_formats['data']:
            data_types = [f"Data files (*.{ext})" for ext in self.available_formats['data']]
            file_types.extend(data_types)

        file_types.append("All files (*.*)")

        return filedialog.asksaveasfilename(
            title="Export Transformation",
            filetypes=file_types,
            defaultextension=".png"
        )

    def _create_progress_window(self, message: str):
        """Create progress window for long operations."""
        self.progress_window = tk.Toplevel(self.parent_widget)
        self.progress_window.title("Export Progress")
        self.progress_window.geometry("400x100")
        self.progress_window.resizable(False, False)

        # Center window
        self.progress_window.transient(self.parent_widget)
        self.progress_window.grab_set()

        # Message label
        ttk.Label(self.progress_window, text=message, font=('Arial', 10)).pack(pady=10)

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        progress_bar = ttk.Progressbar(self.progress_window, variable=self.progress_var,
                                     length=350, mode='determinate')
        progress_bar.pack(pady=10)

        # Status label
        self.status_var = tk.StringVar(value="Starting...")
        ttk.Label(self.progress_window, textvariable=self.status_var).pack(pady=5)

        # Make window modal
        self.progress_window.protocol("WM_DELETE_WINDOW", lambda: None)

    def _close_progress_window(self):
        """Close progress window."""
        if self.progress_window:
            self.progress_window.destroy()
            self.progress_window = None
            self.progress_var = None
            self.status_var = None

    def show_export_dialog(self, transformation_data: Dict[str, Any]) -> None:
        """Show comprehensive export dialog."""
        dialog = tk.Toplevel(self.parent_widget)
        dialog.title("Export Transformation")
        dialog.geometry("500x600")
        dialog.resizable(True, True)

        # Make modal
        dialog.transient(self.parent_widget)
        dialog.grab_set()

        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Export Transformation Analysis",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # Format selection
        format_frame = ttk.LabelFrame(main_frame, text="Export Format", padding=10)
        format_frame.pack(fill=tk.X, pady=(0, 20))

        format_var = tk.StringVar(value="png")
        formats = []

        # Group formats by type
        format_groups = {
            'Images': self.available_formats['image'],
            'Videos': self.available_formats['video'],
            'Reports': self.available_formats['report'],
            'Data': self.available_formats['data']
        }

        for group_name, group_formats in format_groups.items():
            if group_formats:
                ttk.Label(format_frame, text=f"{group_name}:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                for fmt in group_formats:
                    ttk.Radiobutton(format_frame, text=fmt.upper(), variable=format_var,
                                   value=fmt).pack(anchor=tk.W, padx=(20, 0))
                formats.extend(group_formats)

        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Export Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 20))

        include_metadata_var = tk.BooleanVar(value=self.config.include_metadata)
        ttk.Checkbutton(options_frame, text="Include metadata",
                       variable=include_metadata_var).pack(anchor=tk.W)

        include_timestamps_var = tk.BooleanVar(value=self.config.include_timestamps)
        ttk.Checkbutton(options_frame, text="Include timestamps",
                       variable=include_timestamps_var).pack(anchor=tk.W)

        include_byte_analysis_var = tk.BooleanVar(value=self.config.include_byte_analysis)
        ttk.Checkbutton(options_frame, text="Include byte analysis",
                       variable=include_byte_analysis_var).pack(anchor=tk.W)

        # Quality settings (for applicable formats)
        quality_frame = ttk.LabelFrame(main_frame, text="Quality Settings", padding=10)
        quality_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(quality_frame, text="Image Quality:").pack(side=tk.LEFT)
        quality_var = tk.IntVar(value=self.config.quality)
        quality_scale = ttk.Scale(quality_frame, from_=10, to=100, variable=quality_var,
                                orient=tk.HORIZONTAL, length=200)
        quality_scale.pack(side=tk.LEFT, padx=(10, 10))
        quality_label = ttk.Label(quality_frame, text=f"{self.config.quality}%")
        quality_label.pack(side=tk.LEFT)

        def update_quality_label(value):
            quality_label.config(text=f"{int(float(value))}%")
        quality_scale.config(command=update_quality_label)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        def do_export():
            # Update config
            self.config.format_type = format_var.get()
            self.config.include_metadata = include_metadata_var.get()
            self.config.include_timestamps = include_timestamps_var.get()
            self.config.include_byte_analysis = include_byte_analysis_var.get()
            self.config.quality = quality_var.get()

            # Get filename
            filename = filedialog.asksaveasfilename(
                title="Export Transformation",
                defaultextension=f".{self.config.format_type}",
                filetypes=[(f"{self.config.format_type.upper()} files", f"*.{self.config.format_type}")]
            )

            if filename:
                # Export in background thread
                def export_worker():
                    try:
                        success = self.export_transformation_sequence(transformation_data, filename)
                        dialog.after(0, lambda: (
                            messagebox.showinfo("Export Complete", f"Successfully exported to {filename}") if success
                            else None,
                            dialog.destroy()
                        ))
                    except Exception as e:
                        dialog.after(0, lambda: messagebox.showerror("Export Error", f"Failed to export: {e}"))

                threading.Thread(target=export_worker, daemon=True).start()

        ttk.Button(button_frame, text="Export", command=do_export).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        dialog.wait_window()