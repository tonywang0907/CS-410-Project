#!/home/retroflux/anaconda3/bin/python3

#source for CO2e values per power resource
#https://www.cowi.com/news-and-press/news/2023/comparing-co2-emissions-from-different-energy-sources/
carbon_intensity_values = {
   "hydro"        :  4,
   "wind"         :  11,
   "nuclear"      :  12,
   "solar"        :  41,
   "gas_min"      :  290,
   "oil_min"      :  510,
   "coal_min"     :  740,
   "gas_max"      :  930,
   "oil_max"      :  1170,
   "coal_max"     :  1689,
   "fossils_min"  :  1540,
   "fossils_max"  :  3789
}

# Move carbon_mix to top of file with other constants
carbon_mix = {
   "coal": 0.7,
   "wind": 0.1,
   "solar": 0.2              
}

def main():
   #example data (uncomment to run the test data)
   kilojoules_used = 20

   jsc_value_min,jsc_value_max = calculateJobSustainabilityCost(carbon_mix,kilojoules_used)
   print(f"JSC Values")
   print(f"Min: {jsc_value_min:.2f} gCO2e")
   print(f"Max: {jsc_value_max:.2f} gCO2e")

   asc_value_min = amortizedSustainabilityCost(jsc_value_min, 5, 3, 10000)
   asc_value_max = amortizedSustainabilityCost(jsc_value_max, 5, 3, 10000)
   print(f"\nASC Values")
   print(f"Section 2.5 example calculation (expected result ~= 41.9): {amortizedSustainabilityCost(40, 5, 3, 10000):.1f}")
   print(f"Min: {asc_value_min:.2f} gCO2e")
   print(f"Max: {asc_value_max:.2f} gCO2e")

   job_time_in_seconds = 5 #same data, but I've changed the time from 5 hours to 5 seconds for bigger numbers
   scr_value_min = sustainability_cost_rate_per_second(jsc_value_min, job_time_in_seconds)
   scr_value_max = sustainability_cost_rate_per_second(jsc_value_max, job_time_in_seconds)

   print(f"\nSCR Values")
   print(f"Min: {scr_value_min:.2f} gCO2e/s")
   print(f"Max: {scr_value_max:.2f} gCO2e/s")



#JSC cost calculation
def calculateJobSustainabilityCost(percent_carbon_mix, kiloJoulesUsed, estimated_power_and_cooling_losses = 0.08):
   #calculateJobSustainabilityCost
   #Input: 
   #  percent_carbon_mix: dict containing subset of carbon_intensity_vaulues:percentage pairs
   #  kiloJoulesUsed: total estimated power cost for a job to run
   #  estimated_power_and_cooling_losses: estimate on the losses to heat and power inefficiency when running the system.
   #                                      Value defaut set to the one in the paper = 8% efficiency loss
   #Output:
   #  jsc_value:  min and max JSC value based on the proportional energy mix. If no fossil fuels are used,
   #              these values will be equal. This value is in gCO2e (grams CO2 equivalent)
   jsc_value_min = 0
   jsc_value_max = 0
   for energy_source in percent_carbon_mix:
      energy_source_min = energy_source
      energy_source_max = energy_source

      #modify values for fossil fuels to handle the min/max dict values in carbon_intensity_values
      if energy_source in ["coal","oil","gas"]:
         energy_source_min += "_min"
         energy_source_max += "_max"

      jsc_value_min += carbon_intensity_values[energy_source_min]*kiloJoulesUsed*percent_carbon_mix[energy_source]
      jsc_value_max += carbon_intensity_values[energy_source_max]*kiloJoulesUsed*percent_carbon_mix[energy_source]

   #include heat/power losses and convert the kJ to kwh to get the final JSC cost in gCO2e
   jsc_value_max = (jsc_value_max* (1+estimated_power_and_cooling_losses))/3600
   jsc_value_min = (jsc_value_min* (1+estimated_power_and_cooling_losses))/3600

   return (jsc_value_min, jsc_value_max)

def amortizedSustainabilityCost(jsc_value, job_time_hours, estimated_hardware_lifetime_years, lifetime_hardware_embodied_costs):
   # amortizedSustainabilityCost
   # Input: 
   #  jsc_value: float value representing the gCO2e used to run a job
   #  job_time_hours: float value of the time in hours for the job to complete
   #  estimated_hardware_lifetime_years: float value of the estimated/avg life expected for the hardware running the job
   #  lifetime_hardware_embodied_costs: integer value calculating the gCO2e costs for the system
   # Output:
   #  asc_value: float value representing the ASC costs in gCO2e. This is the sum of the jsc_value and the ASC  
   # 
   hardware_hours_available = estimated_hardware_lifetime_years * 365 * 24 # for simplicity, leap years are omitted
   percent_hours_used = job_time_hours/hardware_hours_available

   #amount used for job plus fraction of total hardware gCO2e costs
   asc_value = jsc_value + float(lifetime_hardware_embodied_costs*percent_hours_used) 
   return asc_value  

def sustainability_cost_rate_per_second(jsc_value, time_delta_seconds):
   #converts the jsc value to a seconds-proortional value (ie. gCO2e/s)
   return jsc_value/time_delta_seconds

if __name__ == "__main__":
   main()
