package com.aitrading.realtime.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

@JsonIgnoreProperties(ignoreUnknown = true)
public record CandleEnvelopeDto(
        @NotBlank String entity,
        @NotBlank String source,
        @NotBlank String symbol,
        @NotBlank String timeframe,
        @NotNull @PositiveOrZero @JsonProperty("bucket_epoch") Long bucketEpoch,
        @NotNull @PositiveOrZero @JsonProperty("event_time_ms") Long eventTimeMs,
        @NotNull @Valid CandleOhlcvDto payload
) {
}
