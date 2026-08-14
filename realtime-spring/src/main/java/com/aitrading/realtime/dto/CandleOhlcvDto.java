package com.aitrading.realtime.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

@JsonIgnoreProperties(ignoreUnknown = true)
public record CandleOhlcvDto(
        @NotNull Double open,
        @NotNull Double high,
        @NotNull Double low,
        @NotNull Double close,
        @NotNull @PositiveOrZero Double volume,
        @PositiveOrZero @JsonProperty("trade_count") Integer tradeCount
) {
}
