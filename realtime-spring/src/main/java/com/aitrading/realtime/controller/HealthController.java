package com.aitrading.realtime.controller;

import com.aitrading.realtime.service.CandleQueryService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class HealthController {

    private final CandleQueryService candleQueryService;

    public HealthController(CandleQueryService candleQueryService) {
        this.candleQueryService = candleQueryService;
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        return Map.of(
                "ok", true,
                "service", "realtime-spring",
                "websocketSessions", candleQueryService.openSessionCount()
        );
    }
}
