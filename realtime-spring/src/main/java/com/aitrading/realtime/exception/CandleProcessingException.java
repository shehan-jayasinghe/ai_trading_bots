package com.aitrading.realtime.exception;

public class CandleProcessingException extends ApiException {

    public CandleProcessingException(String message) {
        super("CANDLE_PROCESSING_ERROR", message);
    }

    public CandleProcessingException(String message, Throwable cause) {
        super("CANDLE_PROCESSING_ERROR", message, cause);
    }
}
