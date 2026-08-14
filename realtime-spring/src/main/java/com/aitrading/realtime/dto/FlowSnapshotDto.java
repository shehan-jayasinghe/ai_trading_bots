package com.aitrading.realtime.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record FlowSnapshotDto(
        String symbol,
        String entity,
        String source,
        @JsonProperty("window_sec") Integer windowSec,
        @JsonProperty("bucket_epoch") Long bucketEpoch,
        Double price,
        @JsonProperty("buy_volume") Double buyVolume,
        @JsonProperty("sell_volume") Double sellVolume,
        Double delta,
        @JsonProperty("buy_aggression") Double buyAggression,
        String pressure,
        @JsonProperty("bid_liquidity") Double bidLiquidity,
        @JsonProperty("ask_liquidity") Double askLiquidity,
        @JsonProperty("liquidity_imbalance") Double liquidityImbalance,
        String reaction,
        Map<String, Object> windows
) {
}
