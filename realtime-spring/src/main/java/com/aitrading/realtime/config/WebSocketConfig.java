package com.aitrading.realtime.config;

import com.aitrading.realtime.controller.CandleWebSocketHandler;
import com.aitrading.realtime.controller.FlowWebSocketHandler;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    private final CandleWebSocketHandler candleWebSocketHandler;
    private final FlowWebSocketHandler flowWebSocketHandler;
    private final String websocketPath;
    private final String flowPath;

    public WebSocketConfig(
            CandleWebSocketHandler candleWebSocketHandler,
            FlowWebSocketHandler flowWebSocketHandler,
            @Value("${app.websocket.path:/ws}") String websocketPath,
            @Value("${app.websocket.flow-path:/ws/flow}") String flowPath
    ) {
        this.candleWebSocketHandler = candleWebSocketHandler;
        this.flowWebSocketHandler = flowWebSocketHandler;
        this.websocketPath = websocketPath;
        this.flowPath = flowPath;
    }

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(candleWebSocketHandler, websocketPath).setAllowedOrigins("*");
        registry.addHandler(flowWebSocketHandler, flowPath).setAllowedOrigins("*");
    }
}
