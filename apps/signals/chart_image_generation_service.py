"""
Phase 5.1: Chart Image Generation Service
Generates chart images for ML training and analysis
"""

import logging
import os
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import numpy as np
import pandas as pd
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db.models import Q
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns

from apps.trading.models import Symbol
from apps.data.models import MarketData
from apps.signals.models import ChartImage, ChartPattern, EntryPoint

logger = logging.getLogger(__name__)


class ChartImageGenerationService:
    """Service for generating chart images for ML training and analysis"""
    
    def __init__(self):
        self.chart_config = {
            'width': 800,
            'height': 600,
            'dpi': 100,
            'style': 'dark_background',
            'colors': {
                'bullish': '#00ff88',
                'bearish': '#ff4444',
                'neutral': '#888888',
                'background': '#1a1a1a',
                'grid': '#333333',
                'text': '#ffffff'
            }
        }
        
        # Timeframe configurations
        self.timeframe_configs = {
            '1M': {'candles': 100, 'period': timedelta(minutes=100)},
            '5M': {'candles': 100, 'period': timedelta(minutes=500)},
            '15M': {'candles': 100, 'period': timedelta(minutes=1500)},
            '30M': {'candles': 100, 'period': timedelta(minutes=3000)},
            '1H': {'candles': 100, 'period': timedelta(hours=100)},
            '4H': {'candles': 100, 'period': timedelta(hours=400)},
            '1D': {'candles': 100, 'period': timedelta(days=100)},
            '1W': {'candles': 52, 'period': timedelta(weeks=52)},
        }
    
    def generate_chart_image(self, symbol: Symbol, timeframe: str, 
                           chart_type: str = 'CANDLESTICK',
                           include_patterns: bool = True,
                           include_entry_points: bool = True) -> Optional[ChartImage]:
        """
        Generate a chart image for a specific symbol and timeframe
        
        Args:
            symbol: Trading symbol
            timeframe: Chart timeframe (1M, 5M, 1H, etc.)
            chart_type: Type of chart (CANDLESTICK, LINE, etc.)
            include_patterns: Whether to include pattern annotations
            include_entry_points: Whether to include entry point annotations
            
        Returns:
            ChartImage instance or None if generation fails
        """
        try:
            logger.info(f"Generating {chart_type} chart for {symbol.symbol} - {timeframe}")
            
            # Get market data
            market_data = self._get_market_data(symbol, timeframe)
            if not market_data or len(market_data) < 10:
                logger.warning(f"Insufficient market data for {symbol.symbol} - {timeframe}")
                return None
            
            # Generate chart image
            chart_image = self._create_chart_image(
                symbol, timeframe, market_data, chart_type,
                include_patterns, include_entry_points
            )
            
            if chart_image:
                logger.info(f"Successfully generated chart for {symbol.symbol} - {timeframe}")
                return chart_image
            else:
                logger.error(f"Failed to generate chart for {symbol.symbol} - {timeframe}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating chart for {symbol.symbol} - {timeframe}: {e}")
            return None
    
    def generate_training_dataset(self, symbols: List[Symbol], 
                                timeframes: List[str] = None,
                                days_back: int = 30) -> Dict[str, int]:
        """
        Generate training dataset of chart images for multiple symbols
        
        Args:
            symbols: List of symbols to generate charts for
            timeframes: List of timeframes to generate (default: all)
            days_back: Number of days back to generate charts
            
        Returns:
            Dictionary with generation statistics
        """
        if timeframes is None:
            timeframes = ['1H', '4H', '1D']
        
        stats = {
            'total_generated': 0,
            'failed': 0,
            'symbols_processed': 0,
            'timeframes_processed': 0
        }
        
        logger.info(f"Generating training dataset for {len(symbols)} symbols, {len(timeframes)} timeframes")
        
        for symbol in symbols:
            try:
                stats['symbols_processed'] += 1
                
                for timeframe in timeframes:
                    try:
                        stats['timeframes_processed'] += 1
                        
                        # Generate chart for this symbol/timeframe combination
                        chart_image = self.generate_chart_image(
                            symbol=symbol,
                            timeframe=timeframe,
                            chart_type='CANDLESTICK',
                            include_patterns=True,
                            include_entry_points=True
                        )
                        
                        if chart_image:
                            # Mark as training data
                            chart_image.is_training_data = True
                            chart_image.save()
                            stats['total_generated'] += 1
                        else:
                            stats['failed'] += 1
                            
                    except Exception as e:
                        logger.error(f"Error generating chart for {symbol.symbol} - {timeframe}: {e}")
                        stats['failed'] += 1
                        
            except Exception as e:
                logger.error(f"Error processing symbol {symbol.symbol}: {e}")
                stats['failed'] += 1
        
        logger.info(f"Training dataset generation completed: {stats}")
        return stats
    
    def _get_market_data(self, symbol: Symbol, timeframe: str) -> Optional[List[Dict]]:
        """Get market data for chart generation"""
        try:
            config = self.timeframe_configs.get(timeframe)
            if not config:
                logger.error(f"Unsupported timeframe: {timeframe}")
                return None
            
            # Calculate time range
            end_time = timezone.now()
            start_time = end_time - config['period']
            
            # Get market data
            market_data = MarketData.objects.filter(
                symbol=symbol,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            ).order_by('timestamp')
            
            if not market_data.exists():
                logger.warning(f"No market data found for {symbol.symbol} - {timeframe}")
                return None
            
            # Convert to list of dictionaries
            data_list = []
            for data in market_data:
                data_list.append({
                    'timestamp': data.timestamp,
                    'open': float(data.open_price),
                    'high': float(data.high_price),
                    'low': float(data.low_price),
                    'close': float(data.close_price),
                    'volume': float(data.volume)
                })
            
            # Limit to configured number of candles
            if len(data_list) > config['candles']:
                data_list = data_list[-config['candles']:]
            
            return data_list
            
        except Exception as e:
            logger.error(f"Error getting market data for {symbol.symbol} - {timeframe}: {e}")
            return None
    
    def _create_chart_image(self, symbol: Symbol, timeframe: str, 
                          market_data: List[Dict], chart_type: str,
                          include_patterns: bool, include_entry_points: bool) -> Optional[ChartImage]:
        """Create the actual chart image"""
        try:
            # Set up matplotlib
            plt.style.use(self.chart_config['style'])
            fig, ax = plt.subplots(figsize=(
                self.chart_config['width'] / self.chart_config['dpi'],
                self.chart_config['height'] / self.chart_config['dpi']
            ), dpi=self.chart_config['dpi'])
            
            # Convert data to DataFrame
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Plot chart based on type
            if chart_type == 'CANDLESTICK':
                self._plot_candlestick_chart(ax, df)
            elif chart_type == 'LINE':
                self._plot_line_chart(ax, df)
            else:
                logger.error(f"Unsupported chart type: {chart_type}")
                return None
            
            # Add patterns if requested
            if include_patterns:
                self._add_pattern_annotations(ax, df, symbol, timeframe)
            
            # Add entry points if requested
            if include_entry_points:
                self._add_entry_point_annotations(ax, df, symbol, timeframe)
            
            # Customize chart appearance
            self._customize_chart_appearance(ax, df, symbol, timeframe)
            
            # Save chart to image
            chart_image = self._save_chart_to_image(fig, symbol, timeframe, df)
            
            plt.close(fig)
            return chart_image
            
        except Exception as e:
            logger.error(f"Error creating chart image: {e}")
            return None
    
    def _plot_candlestick_chart(self, ax, df: pd.DataFrame):
        """Plot candlestick chart"""
        try:
            # Calculate candlestick properties
            colors = []
            heights = []
            bottoms = []
            
            for _, row in df.iterrows():
                open_price = row['open']
                close_price = row['close']
                high_price = row['high']
                low_price = row['low']
                
                # Determine color
                if close_price >= open_price:
                    color = self.chart_config['colors']['bullish']
                else:
                    color = self.chart_config['colors']['bearish']
                
                colors.append(color)
                heights.append(abs(close_price - open_price))
                bottoms.append(min(open_price, close_price))
            
            # Plot candlesticks
            x_positions = range(len(df))
            
            # Plot candle bodies
            ax.bar(x_positions, heights, bottom=bottoms, color=colors, width=0.8)
            
            # Plot wicks
            for i, (_, row) in enumerate(df.iterrows()):
                high_price = row['high']
                low_price = row['low']
                open_price = row['open']
                close_price = row['close']
                
                # Upper wick
                upper_wick_height = high_price - max(open_price, close_price)
                if upper_wick_height > 0:
                    ax.bar(i, upper_wick_height, bottom=max(open_price, close_price), 
                          color=colors[i], width=0.1)
                
                # Lower wick
                lower_wick_height = min(open_price, close_price) - low_price
                if lower_wick_height > 0:
                    ax.bar(i, lower_wick_height, bottom=low_price, 
                          color=colors[i], width=0.1)
            
        except Exception as e:
            logger.error(f"Error plotting candlestick chart: {e}")
    
    def _plot_line_chart(self, ax, df: pd.DataFrame):
        """Plot line chart"""
        try:
            x_positions = range(len(df))
            ax.plot(x_positions, df['close'], color=self.chart_config['colors']['neutral'], linewidth=2)
        except Exception as e:
            logger.error(f"Error plotting line chart: {e}")
    
    def _add_pattern_annotations(self, ax, df: pd.DataFrame, symbol: Symbol, timeframe: str):
        """Add pattern annotations to chart"""
        try:
            # Get existing patterns for this symbol/timeframe
            patterns = ChartPattern.objects.filter(
                chart_image__symbol=symbol,
                chart_image__timeframe=timeframe,
                confidence_score__gte=0.7
            ).order_by('-confidence_score')[:5]  # Top 5 patterns
            
            for pattern in patterns:
                # Calculate position on chart
                x_pos = pattern.x_start * len(df)
                y_pos = pattern.y_start * (df['high'].max() - df['low'].min()) + df['low'].min()
                
                # Add pattern annotation
                ax.annotate(
                    pattern.pattern_type,
                    xy=(x_pos, y_pos),
                    xytext=(x_pos + 10, y_pos + 10),
                    arrowprops=dict(arrowstyle='->', color='yellow'),
                    fontsize=8,
                    color='yellow',
                    weight='bold'
                )
                
        except Exception as e:
            logger.error(f"Error adding pattern annotations: {e}")
    
    def _add_entry_point_annotations(self, ax, df: pd.DataFrame, symbol: Symbol, timeframe: str):
        """Add entry point annotations to chart"""
        try:
            # Get existing entry points for this symbol/timeframe
            entry_points = EntryPoint.objects.filter(
                chart_image__symbol=symbol,
                chart_image__timeframe=timeframe,
                confidence_score__gte=0.7
            ).order_by('-confidence_score')[:3]  # Top 3 entry points
            
            for entry_point in entry_points:
                # Calculate position on chart
                x_pos = entry_point.entry_x * len(df)
                y_pos = entry_point.entry_y * (df['high'].max() - df['low'].min()) + df['low'].min()
                
                # Determine color based on entry type
                if entry_point.entry_type in ['BUY', 'BUY_LIMIT', 'BUY_STOP']:
                    color = self.chart_config['colors']['bullish']
                    marker = '^'
                else:
                    color = self.chart_config['colors']['bearish']
                    marker = 'v'
                
                # Add entry point annotation
                ax.scatter(x_pos, y_pos, color=color, marker=marker, s=100, zorder=5)
                ax.annotate(
                    f"{entry_point.entry_type}\n{entry_point.confidence_score:.2f}",
                    xy=(x_pos, y_pos),
                    xytext=(x_pos + 5, y_pos + 5),
                    fontsize=8,
                    color=color,
                    weight='bold'
                )
                
        except Exception as e:
            logger.error(f"Error adding entry point annotations: {e}")
    
    def _customize_chart_appearance(self, ax, df: pd.DataFrame, symbol: Symbol, timeframe: str):
        """Customize chart appearance"""
        try:
            # Set title
            ax.set_title(f"{symbol.symbol} - {timeframe} Chart", 
                        color=self.chart_config['colors']['text'], fontsize=14, weight='bold')
            
            # Set labels
            ax.set_xlabel("Time", color=self.chart_config['colors']['text'])
            ax.set_ylabel("Price", color=self.chart_config['colors']['text'])
            
            # Set colors
            ax.set_facecolor(self.chart_config['colors']['background'])
            ax.tick_params(colors=self.chart_config['colors']['text'])
            
            # Set grid
            ax.grid(True, color=self.chart_config['colors']['grid'], alpha=0.3)
            
            # Format x-axis
            ax.set_xticks(range(0, len(df), max(1, len(df) // 10)))
            ax.set_xticklabels([df.iloc[i]['timestamp'].strftime('%H:%M') 
                              for i in range(0, len(df), max(1, len(df) // 10))])
            
            # Rotate x-axis labels
            plt.setp(ax.get_xticklabels(), rotation=45)
            
        except Exception as e:
            logger.error(f"Error customizing chart appearance: {e}")
    
    def _save_chart_to_image(self, fig, symbol: Symbol, timeframe: str, df: pd.DataFrame) -> Optional[ChartImage]:
        """Save chart to image file and create ChartImage instance"""
        try:
            # Save to BytesIO
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', 
                       facecolor=self.chart_config['colors']['background'],
                       edgecolor='none', dpi=self.chart_config['dpi'])
            img_buffer.seek(0)
            
            # Create filename
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{symbol.symbol}_{timeframe}_{timestamp}.png"
            
            # Create ChartImage instance
            chart_image = ChartImage(
                symbol=symbol,
                chart_type='CANDLESTICK',
                timeframe=timeframe,
                image_width=self.chart_config['width'],
                image_height=self.chart_config['height'],
                start_time=df.iloc[0]['timestamp'],
                end_time=df.iloc[-1]['timestamp'],
                candles_count=len(df),
                price_range_low=Decimal(str(df['low'].min())),
                price_range_high=Decimal(str(df['high'].max())),
                current_price=Decimal(str(df.iloc[-1]['close'])),
                is_training_data=False,
                is_validated=False
            )
            
            # Save image file
            chart_image.image_file.save(filename, ContentFile(img_buffer.getvalue()), save=False)
            chart_image.save()
            
            return chart_image
            
        except Exception as e:
            logger.error(f"Error saving chart to image: {e}")
            return None

