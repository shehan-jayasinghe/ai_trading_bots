package com.aitrading.realtime.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.validation.constraints.Pattern;

@JsonIgnoreProperties(ignoreUnknown = true)
public record ClientFilterDto(
        @Pattern(regexp = "^(btc|gold)?$", message = "entity must be btc or gold")
        String entity,
        @Pattern(regexp = "^\\d+[smh]?$", message = "timeframe must look like 1s, 2s, 1m")
        String timeframe
) {
    public boolean matches(CandleEnvelopeDto candle) {
        if (entity != null && !entity.isBlank() && !entity.equalsIgnoreCase(candle.entity())) {
            return false;
        }
        if (timeframe != null && !timeframe.isBlank() && !timeframe.equalsIgnoreCase(candle.timeframe())) {
            return false;
        }
        return true;
    }
}
