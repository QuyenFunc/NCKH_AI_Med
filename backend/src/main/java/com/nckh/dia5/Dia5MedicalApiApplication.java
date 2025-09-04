package com.nckh.dia5;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

@SpringBootApplication
@EnableJpaAuditing
public class Dia5MedicalApiApplication {

    public static void main(String[] args) {
        SpringApplication.run(Dia5MedicalApiApplication.class, args);
    }
}
