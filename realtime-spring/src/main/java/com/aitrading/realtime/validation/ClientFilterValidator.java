package com.aitrading.realtime.validation;

import com.aitrading.realtime.dto.ClientFilterDto;
import com.aitrading.realtime.exception.ApiException;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validator;
import org.springframework.stereotype.Component;

import java.util.Set;
import java.util.stream.Collectors;

@Component
public class ClientFilterValidator {

    private final Validator validator;

    public ClientFilterValidator(Validator validator) {
        this.validator = validator;
    }

    public ClientFilterDto validate(ClientFilterDto filter) {
        ClientFilterDto safe = filter != null ? filter : new ClientFilterDto(null, null);
        Set<ConstraintViolation<ClientFilterDto>> violations = validator.validate(safe);
        if (!violations.isEmpty()) {
            String message = violations.stream()
                    .map(ConstraintViolation::getMessage)
                    .collect(Collectors.joining("; "));
            throw new ApiException("INVALID_FILTER", message);
        }
        return safe;
    }
}
