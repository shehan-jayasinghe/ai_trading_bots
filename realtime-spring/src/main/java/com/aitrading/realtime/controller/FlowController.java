package com.aitrading.realtime.controller;

import com.aitrading.realtime.dto.FlowSnapshotDto;
import com.aitrading.realtime.service.FlowQueryService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/flow")
public class FlowController {

    private final FlowQueryService flowQueryService;

    public FlowController(FlowQueryService flowQueryService) {
        this.flowQueryService = flowQueryService;
    }

    @GetMapping
    public ResponseEntity<FlowSnapshotDto> latest(
            @RequestParam(defaultValue = "BTCUSDT") String symbol
    ) {
        return flowQueryService.latest(symbol)
                .map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.noContent().build());
    }

    @GetMapping("/all")
    public Map<String, FlowSnapshotDto> all() {
        return flowQueryService.all();
    }
}
