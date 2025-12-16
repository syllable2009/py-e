# 使用 OpenJDK 官方镜像运行应用
FROM openjdk:11-jre-slim

WORKDIR /app

COPY kit-app/target/kit-app-1.0.0.jar  app.jar

# 暴露应用所需的端口
EXPOSE 8080

# 设置默认命令运行应用
ENTRYPOINT ["java", "-jar", "app.jar"]
ENTRYPOINT ["java","-Xms256m","-Xmx256m","-jar","app.jar","--spring.profiles.active=prod","-c"]
