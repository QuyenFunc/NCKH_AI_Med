package com.nckh.dia5.dto.blockchain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SerialNumberStatusDto {

    private boolean exists;

    private boolean redeemed;

    private Long redeemedAt;

    private String redeemedBy;
}
