package com.aitrading.realtime.controller;

import com.aitrading.realtime.service.CandleQueryService;
import com.aitrading.realtime.service.FlowQueryService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class HealthController {

    private final CandleQueryService candleQueryService;
    private final FlowQueryService flowQueryService;

    public HealthController(CandleQueryService candleQueryService, FlowQueryService flowQueryService) {
        this.candleQueryService = candleQueryService;
        this.flowQueryService = flowQueryService;
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        return Map.of(
                "ok", true,
                "service", "realtime-spring",
                "websocketSessions", candleQueryService.openSessionCount(),
                "flowWebsocketSessions", flowQueryService.openSessionCount()
        );
    }
}
