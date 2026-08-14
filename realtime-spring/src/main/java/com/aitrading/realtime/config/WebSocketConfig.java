package com.aitrading.realtime.config;

import com.aitrading.realtime.controller.CandleWebSocketHandler;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    private final CandleWebSocketHandler candleWebSocketHandler;
    private final String websocketPath;

    public WebSocketConfig(
            CandleWebSocketHandler candleWebSocketHandler,
            @Value("${app.websocket.path:/ws}") String websocketPath
    ) {
        this.candleWebSocketHandler = candleWebSocketHandler;
        this.websocketPath = websocketPath;
    }

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(candleWebSocketHandler, websocketPath)
                .setAllowedOrigins("*");
    }
}
