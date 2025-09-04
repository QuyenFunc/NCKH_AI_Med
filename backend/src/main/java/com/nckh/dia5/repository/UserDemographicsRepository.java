package com.nckh.dia5.repository;

import com.nckh.dia5.model.UserDemographics;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserDemographicsRepository extends JpaRepository<UserDemographics, Long> {
    
    Optional<UserDemographics> findByUserId(String userId);
    
    @Query("SELECT COUNT(ud) FROM UserDemographics ud WHERE ud.gender = :gender")
    long countByGender(@Param("gender") UserDemographics.Gender gender);
    
    @Query("SELECT AVG(YEAR(CURRENT_DATE) - ud.birthYear) FROM UserDemographics ud")
    Double getAverageAge();
}
