package com.aitrading.realtime.validation;

import com.aitrading.realtime.dto.CandleEnvelopeDto;
import com.aitrading.realtime.exception.ApiException;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validator;
import org.springframework.stereotype.Component;

import java.util.Set;
import java.util.stream.Collectors;

@Component
public class CandleEnvelopeValidator {

    private final Validator validator;

    public CandleEnvelopeValidator(Validator validator) {
        this.validator = validator;
    }

    public CandleEnvelopeDto validate(CandleEnvelopeDto dto) {
        Set<ConstraintViolation<CandleEnvelopeDto>> violations = validator.validate(dto);
        if (!violations.isEmpty()) {
            String message = violations.stream()
                    .map(ConstraintViolation::getMessage)
                    .collect(Collectors.joining("; "));
            throw new ApiException("INVALID_CANDLE", message);
        }
        return dto;
    }
}
