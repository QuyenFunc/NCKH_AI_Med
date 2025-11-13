package com.nckh.dia5.dto.blockchain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DrugVerificationResultDto {

    private DrugBatchDto batch;

    private SerialNumberStatusDto serialStatus;

    private String serialNumber;

    private boolean newlyRedeemed;
}
