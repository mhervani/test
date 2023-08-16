

#Denne funksjonen starter automatisk optimalisering basert på et tidligere valg og kjører funksjonene under basert på regionskoden som har blitt gitt /mathilde
def start_automatic_optimization(pm, ss, plan, examination, site, region_code, total_dose, fraction_dose, po, opt):
  if opt == 'oar': # Start adaptive optimization for palliative treatments if indicated 
    adapt_optimization_oar(ss, plan, site.oar_objectives, region_code)
    for i in range(0,4):
      adapt_optimization_palliative_second_phase(pm, ss, plan, total_dose)
      po.RunOptimization()
  elif opt == 'auto': # Start automatic iterative optimization if indicated
    for i in range(0,4):
      if region_code in RC.breast_codes:
        adapt_optimization_breast_auto(ss, plan, region_code) #Denne er relevant her /mathilde
      elif region_code in RC.prostate_codes:
        print("-----------------------------Første fase, runde " + str(i))
        adapt_optimization_prostate_auto(ss, plan, region_code)
      elif region_code in RC.gyn_codes:
        adapt_optimization_gyn_auto(ss, plan, region_code, fraction_dose, i)
      nr_it = 40
      if i ==0:
        nr_it = 40
      elif i==1:
        nr_it = 100 
      elif i==3:
        nr_it = 40
       
      po.OptimizationParameters.Algorithm.MaxNumberOfIterations = nr_it
      po.RunOptimization()
    for i in range(0,5):
      nr_it = 40
      po.OptimizationParameters.Algorithm.MaxNumberOfIterations = nr_it
      if region_code in RC.breast_codes:
        adapt_optimization_breast_auto_second_phase(pm, ss, plan, region_code, total_dose, i) #Denne er relevant her /mathilde
      elif region_code in RC.prostate_codes:
        adapt_optimization_prostate_auto_second_phase(pm, ss, plan, examination, region_code, total_dose, i)
      elif region_code in RC.gyn_codes:
        nr_it = 50
        adapt_optimization_gyn_auto_second_phase(pm, ss, plan, examination, region_code, total_dose, i)
      po.RunOptimization()


#Denne funksjonen kjører da først (se over) for å få ned dosen til risikoorganer /mathilde
def adapt_optimization_breast_auto(ss, plan, region_code):
  for i, beam_set in enumerate(plan.BeamSets):
    if region_code in RC.breast_reg_l_codes:
      oar_names = [ROIS.breast_r.name, ROIS.lung_l.name, ROIS.lung_r.name, ROIS.esophagus.name, ROIS.trachea.name, ROIS.thyroid.name, ROIS.humeral_l.name, ROIS.a_lad.name]
    elif region_code in RC.breast_reg_r_codes:
      oar_names = [ROIS.breast_l.name, ROIS.lung_l.name, ROIS.lung_r.name, ROIS.esophagus.name, ROIS.trachea.name, ROIS.thyroid.name, ROIS.humeral_r.name, ROIS.heart.name]
    elif region_code in RC.breast_tang_and_partial_l_codes:
      oar_names = [ROIS.breast_r.name, ROIS.lung_l.name, ROIS.lung_r.name, ROIS.a_lad.name]
    elif region_code in RC.breast_tang_and_partial_r_codes:
      oar_names = [ROIS.breast_l.name, ROIS.lung_l.name, ROIS.lung_r.name, ROIS.heart.name]
    # Get OAR average doses of first optimization, and set the initial OAR target average dose as half of that value:
    for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
      try:
        if o.ForRegionOfInterest.Name in oar_names and o.DoseFunctionParameters.FunctionType == "MaxEud":
          avg = o.OfDoseDistributions[0].GetDoseStatistic(RoiName = o.ForRegionOfInterest.Name, DoseType = 'Average')
          if o.ForRegionOfInterest.Name == ROIS.heart.name:
            if avg > 140:
              o.DoseFunctionParameters.DoseLevel = 100
            else:
              o.DoseFunctionParameters.DoseLevel = 0.7 * avg
          else:    
            o.DoseFunctionParameters.DoseLevel = 0.7 * avg
        elif o.ForRegionOfInterest.Name in oar_names and o.DoseFunctionParameters.FunctionType == "MaxDvh":
          vad = round(o.OfDoseDistributions[0].GetRelativeVolumeAtDoseValues(RoiName=o.ForRegionOfInterest.Name, DoseValues=[200])[0]*100,0)
          o.DoseFunctionParameters.PercentVolume = 0.7*vad
      except:
        print ("Dette er ikke et relevant objective")


#Denne funksjonen kjører etter den forrige for å gjenvinne dekning /mathilde
def adapt_optimization_breast_auto_second_phase(pm, ss, plan, region_code, total_dose, iterations):
  bilateral = False
  if SSF.has_roi_with_shape(ss, ROIS.ptv_pc_l.name) and SSF.has_roi_with_shape(ss, ROIS.ptv_pc_r.name):
    bilateral = True
  # Only first iteration 
  if iterations == 0:
    # Breast boost
    if region_code in RC.breast_partial_codes:
      ctv = [ROIS.ctv_boost.name, ROIS.ctv_boost_r.name, ROIS.ctv_boost_l.name]
    else: # All other cases
      if bilateral:
        ctv = [ROIS.ctv_r.name, ROIS.ctv_l.name, ROIS.ctv_n_r.name, ROIS.ctv_n_l.name, ROIS.ctv_imn_r.name, ROIS.ctv_imn_l.name]
      else:
        ctv = [ROIS.ctv_r.name, ROIS.ctv_l.name, ROIS.ctv_n_r.name, ROIS.ctv_n_l.name, ROIS.ctv_imn_r.name, ROIS.ctv_imn_l.name] #har endret

    # Change weight of UniformDose objective for existing CTV's
    for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
      for i in range(len(ctv)):
        if SSF.has_roi_with_shape(ss, ctv[i]):
          change_objective_weight(o, ctv[i], 300, "UniformDose")
    # Add target EUD objective for existing CTV's
    for i in range(len(ctv)):
      if SSF.has_roi_with_shape(ss, ctv[i]):
        target_eud(ss, plan, ctv[i], total_dose*100, 1, 3000)

  # Create roi from dose and add max dose objective
  if region_code in RC.breast_partial_codes: # Breast boost
    try:
      PMF.create_roi_from_dose(pm, ss, plan, '16.3', 'Blue', 1635)
      max_dose(ss, plan, '16.3', 1650, 10000)
      PMF.exclude_roi_from_export(pm, '16.3')
    except:
      print("No dose > 16.35 Gy")
  else: # All other cases
    try:
      PMF.create_roi_from_dose(pm, ss, plan, '41', 'Blue', 4100)
      max_dose(ss, plan, '41', 4150, 10000)
      PMF.exclude_roi_from_export(pm, '41')
    except:
      print("No dose > 41 Gy")
    #PMF.delete_roi(pm, '42')
    try:
      PMF.create_roi_from_dose(pm, ss, plan, '42', 'Red', 4180)
      max_dose(ss, plan, '42', 4180, 10000) #41.8
      PMF.exclude_roi_from_export(pm, '42')
    except:
      print("No dose > 41.8 Gy")

  # Change weight on PTV min dose objectives based on difference in dose between wanted and current dose
  if region_code in RC.breast_partial_codes: # Boost
    for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
      ptv_boost_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_boost.name, "MinDose", 1525, 0.98, False)
      if ptv_boost_weight:
        break
    for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
      ptv_boost_r_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_boost_r.name, "MinDose", 1525, 0.98, False)
      if ptv_boost_r_weight:
        break
    for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
      ptv_boost_l_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_boost_l.name, "MinDose", 1525, 0.98, False)
      if ptv_boost_l_weight:
        break
  else:
    if bilateral: # Bilateral
      for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
        ptv_pc_r_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_pc_r.name, "MinDose", 3810, 0.99, False)
        #messagebox.showinfo("", str(ptv_pc_r_weight))
        if ptv_pc_r_weight:
          break
      for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
        ptv_pc_l_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_pc_l.name, "MinDose", 3810, 0.99, False)
        if ptv_pc_l_weight:
          break
      for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
        ptv_nc_r_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_nc_r.name, "MinDose", 3810, 0.98, False)
        if ptv_nc_r_weight:
          break
      for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
        ptv_nc_l_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_nc_l.name, "MinDose", 3810, 0.98, False)
        if ptv_nc_l_weight:
          break
      for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
        ptv_n_imn_r_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_n_imn_r.name, "MinDose", 3810, 0.98, False)
        if ptv_n_imn_r_weight:
          break
      for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
        ptv_n_imn_l_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_n_imn_l.name, "MinDose", 3810, 0.98, False)
        if ptv_n_imn_l_weight:
          break
    else: # One sided
      for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
        if SSF.has_roi_with_shape(ss, ROIS.ptv_pc_r.name):#if ROIS.ptv_pc_r.name == "PTVc_breast_R_40":
            ptv_pc_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_pc_r.name, "MinDose", 3810, 0.99, False)
        elif SSF.has_roi_with_shape(ss, ROIS.ptv_pc_l.name):#ROIS.ptv_pc_l.name == "PTVc_breast_L_40":
            ptv_pc_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_pc_l.name, "MinDose", 3810, 0.99, False)
        if ptv_pc_weight:
          break
      for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
        if SSF.has_roi_with_shape(ss, ROIS.ptv_nc_r.name):
            ptv_nc_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_nc_r.name, "MinDose", 3810, 0.99, False) #endret fra 98 til 99
            print(ptv_nc_weight)
        if SSF.has_roi_with_shape(ss, ROIS.ptv_nc_l.name):
            ptv_nc_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_nc_l.name, "MinDose", 3810, 0.99, False)#endret fra 98 til 99
        if ptv_nc_weight:
          break
      for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:
        ptv_n_imn_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_n_imn_r.name, "MinDose", 3810, 0.99, False)#endret fra 98 til 99
        if SSF.has_roi_with_shape(ss, ROIS.ptv_n_imn_r.name):
            ptv_n_imn_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_n_imn_r.name, "MinDose", 3810, 0.99, False)#endret fra 98 til 99
        if SSF.has_roi_with_shape(ss, ROIS.ptv_n_imn_l.name):
            ptv_n_imn_weight = change_objective_weight_based_on_dose_difference_auto(o, ROIS.ptv_n_imn_l.name, "MinDose", 3810, 0.99, False)#endret fra 98 til 99
        if ptv_n_imn_weight:
          break
      
  # Change weight on CTV min dose objective to corresponding PTV weight
  for o in plan.PlanOptimizations[0].Objective.ConstituentFunctions:  
    if region_code in RC.breast_partial_codes:
      change_objective_weight(o, ROIS.ctv_boost.name, ptv_boost_weight, "MinDose")
      change_objective_weight(o, ROIS.ctv_boost_r.name, ptv_boost_r_weight, "MinDose")
      change_objective_weight(o, ROIS.ctv_boost_l.name, ptv_boost_l_weight, "MinDose")
    else:
      if bilateral:
        change_objective_weight(o, ROIS.ctv_r.name, ptv_pc_r_weight, "MinDose")
        change_objective_weight(o, ROIS.ctv_l.name, ptv_pc_l_weight, "MinDose")
        change_objective_weight(o, ROIS.ctv_n_r.name, ptv_nc_r_weight, "MinDose")
        change_objective_weight(o, ROIS.ctv_n_l.name, ptv_nc_l_weight, "MinDose")
        change_objective_weight(o, ROIS.ctv_imn_l.name, ptv_n_imn_l_weight, "MinDose")
        change_objective_weight(o, ROIS.ctv_imn_r.name, ptv_n_imn_r_weight, "MinDose")
      else:
        if ROIS.ctv_r.name == "CTV_breast_R_40":
            change_objective_weight(o, ROIS.ctv_r.name, ptv_pc_weight, "MinDose")
            change_objective_weight(o, ROIS.ctv_n_r.name, ptv_nc_weight, "MinDose")
            print(ptv_nc_weight)
            change_objective_weight(o, ROIS.ctv_imn_r.name, ptv_n_imn_weight, "MinDose")
        #change_objective_weight(o, ROIS.ctv_p.name, roi_weight_dict[ROIS.ptv_pc.name], "MinDose")
        elif ROIS.ctv_l.name == "CTV_breast_L_40":
            change_objective_weight(o, ROIS.ctv_l.name, ptv_pc_weight, "MinDose")
            change_objective_weight(o, ROIS.ctv_n_l.name, ptv_nc_weight, "MinDose")
            change_objective_weight(o, ROIS.ctv_imn_l.name, ptv_n_imn_weight, "MinDose")


#Denne funksjonen brukes i funksjonen ovenfor for å beregne hvordan vekten på objektivet skal endres /mathilde

# Change weight for given ROI min dose objectives based on difference in dose between wanted and current dose
def change_objective_weight_based_on_dose_difference_auto(o, roi_name, function_type, dose_goal, volume, use_robustness):
  try:
    if o.ForRegionOfInterest.Name == roi_name and o.DoseFunctionParameters.FunctionType == function_type and o.UseRobustness == use_robustness:
      d = o.OfDoseDistributions[0].GetDoseAtRelativeVolumes(RoiName = o.ForRegionOfInterest.Name, RelativeVolumes = [volume])[0]
      weight = round(((dose_goal-d)*2.5*o.DoseFunctionParameters.Weight)/100,0)+o.DoseFunctionParameters.Weight
      if weight != 'None' and weight > 0:
        o.DoseFunctionParameters.Weight = weight
        #messagebox.showinfo("", "ptv" + str(weight))
        return weight
  except:
    print ("Dette er ikke et relevant objective")