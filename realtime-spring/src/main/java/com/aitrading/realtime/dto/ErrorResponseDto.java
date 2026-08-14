package com.aitrading.realtime.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record ErrorResponseDto(
        String code,
        String message,
        String path
) {
}
