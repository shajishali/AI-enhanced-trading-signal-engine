from django.contrib import admin
from .models import SignalType, AIModel, Signal, SignalExecution, ModelPerformance


@admin.register(SignalType)
class SignalTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'version', 'accuracy', 'is_active', 'created_at']
    list_filter = ['model_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'signal_direction', 'confidence_level', 'confidence_score', 'ai_model', 'is_active', 'generated_at']
    list_filter = ['signal_direction', 'confidence_level', 'is_active', 'generated_at']
    search_fields = ['symbol__symbol', 'ai_model__name']
    readonly_fields = ['generated_at']


@admin.register(SignalExecution)
class SignalExecutionAdmin(admin.ModelAdmin):
    list_display = ['signal', 'user', 'execution_price', 'quantity', 'executed_at']
    list_filter = ['executed_at']
    search_fields = ['signal__symbol__symbol', 'user__username']
    readonly_fields = ['executed_at']


@admin.register(ModelPerformance)
class ModelPerformanceAdmin(admin.ModelAdmin):
    list_display = ['ai_model', 'symbol', 'total_signals', 'correct_signals', 'accuracy', 'total_pnl', 'last_updated']
    list_filter = ['ai_model', 'last_updated']
    search_fields = ['ai_model__name', 'symbol__symbol']
    readonly_fields = ['last_updated']
