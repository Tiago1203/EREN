"""PHASE 7 - EPIC 4: Monitoring & Observability Tests."""
from datetime import datetime, timedelta

class TestPrometheusMetrics:
    def test_counter_inc(self):
        from core.PHASE_7.observability import PrometheusMetricsRegistry
        r = PrometheusMetricsRegistry()
        c = r.counter("req", "Requests", ["method"])
        c.inc(method="GET")
        assert c.get_value(method="GET") == 1

    def test_gauge_set_inc(self):
        from core.PHASE_7.observability import PrometheusMetricsRegistry
        r = PrometheusMetricsRegistry()
        g = r.gauge("users", "Active users")
        g.set(10); g.inc()
        assert g.get_value() == 11

    def test_render_prometheus(self):
        from core.PHASE_7.observability import PrometheusMetricsRegistry
        r = PrometheusMetricsRegistry()
        c = r.counter("req", "Requests", ["method"])
        c.inc(method="GET")
        output = r.render_prometheus()
        assert "HELP eren_req" in output

class TestMetricsCollector:
    def test_record_http(self):
        from core.PHASE_7.observability import MetricsCollector
        mc = MetricsCollector()
        mc.record_http_request("GET", "/api", 200, 45.0, "t1")
        mc.record_llm_request("gpt-4", 100, 50, 500.0, True, "t1")
        mc.record_health_check("api", "healthy", 10.0, "t1")
        assert True

class TestLogAggregator:
    def test_ingest_and_query(self):
        from core.PHASE_7.observability import LogAggregator, LogSource
        la = LogAggregator()
        la.ingest("INFO", LogSource.APPLICATION, "Test", "t1")
        la.ingest("ERROR", LogSource.API, "Error", "t2")
        results = la.query(tenant_id="t1")
        assert len(results) == 1

    def test_stats(self):
        from core.PHASE_7.observability import LogAggregator, LogSource
        la = LogAggregator()
        la.ingest("INFO", LogSource.APPLICATION, "Test", "t1")
        stats = la.get_stats()
        assert stats["total_entries"] == 1

class TestDistributedTracer:
    def test_span_lifecycle(self):
        from core.PHASE_7.observability import DistributedTracer, SpanKind
        tracer = DistributedTracer("test")
        span = tracer.start_span("test-span", kind=SpanKind.SERVER)
        span.set_attribute("tenant_id", "t1"); span.end(); tracer.end_span(span)
        assert len(tracer._spans) == 1

class TestAlertManager:
    def test_setup_default_rules(self):
        from core.PHASE_7.observability import AlertManager
        am = AlertManager()
        am.setup_default_rules()
        assert len(am._rules) >= 5

    def test_fire_alert(self):
        from core.PHASE_7.observability import AlertManager
        am = AlertManager()
        am.setup_default_rules()
        alert = am.fire_alert("high-error-rate", "Error rate exceeded")
        assert alert is not None
        assert am.get_alert_summary()["firing"] == 1

    def test_resolve_alert(self):
        from core.PHASE_7.observability import AlertManager, AlertStatus
        am = AlertManager()
        am.setup_default_rules()
        alert = am.fire_alert("high-error-rate", "Test")
        resolved = am.resolve_alert(alert.alert_id)
        assert resolved.status == AlertStatus.RESOLVED

class TestSLOManager:
    def test_add_slo(self):
        from core.PHASE_7.observability import SLOManager, SLO, SLIMetric
        slo_mgr = SLOManager()
        slo = SLO("slo-1", "Test SLO", SLIMetric.AVAILABILITY, 99.9, 30)
        slo_mgr.add_slo(slo)
        assert len(slo_mgr._slos) == 1

    def test_record_measurement(self):
        from core.PHASE_7.observability import SLOManager, SLO, SLIMetric, SLOStatus
        slo_mgr = SLOManager()
        slo = SLO("slo-1", "Test SLO", SLIMetric.AVAILABILITY, 99.9, 30)
        slo_mgr.add_slo(slo)
        now = datetime.now()
        slo_mgr.record_measurement("slo-1", 99.95, now - timedelta(hours=1))
        status = slo_mgr.get_current_status("slo-1")
        assert status is not None
        assert status.status in (SLOStatus.HEALTHY, SLOStatus.AT_RISK, SLOStatus.BREACHED)

class TestOperationsDashboard:
    def test_overview(self):
        from core.PHASE_7.observability import OperationsDashboard
        dash = OperationsDashboard()
        overview = dash.get_overview()
        assert "system_status" in overview

    def test_services(self):
        from core.PHASE_7.observability import OperationsDashboard
        dash = OperationsDashboard()
        services = dash.get_services_status()
        assert len(services) >= 5

    def test_grafana_dashboard(self):
        from core.PHASE_7.observability import OperationsDashboard
        dash = OperationsDashboard()
        grafana = dash.get_grafana_dashboard_json()
        assert "panels" in grafana
        assert grafana["title"] == "EREN Operations Dashboard"
