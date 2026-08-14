package com.aitrading.realtime.controller;

import com.aitrading.realtime.dto.CandleEnvelopeDto;
import com.aitrading.realtime.service.CandleQueryService;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/candles")
@Validated
public class CandleHistoryController {

    private final CandleQueryService candleQueryService;

    public CandleHistoryController(CandleQueryService candleQueryService) {
        this.candleQueryService = candleQueryService;
    }

    @GetMapping
    public List<CandleEnvelopeDto> recent(
            @RequestParam @NotBlank @Pattern(regexp = "^(btc|gold)$") String entity,
            @RequestParam @NotBlank @Pattern(regexp = "^\\d+[smh]$") String timeframe
    ) {
        return candleQueryService.recent(entity, timeframe);
    }
}
