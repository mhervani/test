
#Denne funksjonen oppretter start-objectives for planen basert på strukturnavn og regionskode

# BREAST
def create_breast_objectives(ss, plan, region_code, total_dose, technique_name, opt):
  if region_code in RC.breast_l_codes: # Left
    contralateral_lung = ROIS.lung_r.name
    ipsilateral_lung = ROIS.lung_l.name
    contralateral_breast = ROIS.breast_r.name
    ipsilateral_humeral = ROIS.humeral_l.name
  else: # Right
    contralateral_lung = ROIS.lung_l.name
    ipsilateral_lung = ROIS.lung_r.name
    contralateral_breast = ROIS.breast_l.name
    ipsilateral_humeral = ROIS.humeral_r.name
  index = 0
  if technique_name == '3D-CRT': # For hybrid boost (because of two beam sets)
    index = 1
  if region_code in RC.breast_partial_codes: # Breast boost 2 Gy x 8
    ctv = [ROIS.ctv_boost.name, ROIS.ctv_boost_r.name, ROIS.ctv_boost_l.name]
    ptv = [ROIS.ptv_boost.name, ROIS.ptv_boost_r.name, ROIS.ptv_boost_l.name]
    for i in range(len(ctv)):
      if SSF.has_roi_with_shape(ss, ctv[i]):
        OF.uniform_dose(ss, plan, ctv[i], total_dose*100, 10, beam_set_index = index)
    for i in range(len(ptv)):
      if SSF.has_roi_with_shape(ss, ptv[i]):
        OF.min_dose(ss, plan, ptv[i], 0.95*total_dose*100, 1000, beam_set_index = index)
    OF.fall_off(ss, plan, ROIS.body.name, total_dose*100, total_dose/2*100, 1, 1, beam_set_index = index)
    OF.max_dose(ss, plan, ROIS.body.name, 1.035*total_dose*100, 30000, beam_set_index = index)
    if SSF.has_roi_with_shape(ss, contralateral_breast):
      OF.max_eud(ss, plan, contralateral_breast, 0.1*100, 1, 1, beam_set_index = index)
    OF.max_dvh(ss, plan, ipsilateral_lung, 0.5*100, 35, 1, beam_set_index = index)
    OF.max_eud(ss, plan, ipsilateral_lung, 1*100, 1, 1, beam_set_index = index)
    OF.max_eud(ss, plan, contralateral_lung, 0.1*100, 1, 1, beam_set_index = index)
    OF.max_eud(ss, plan, ROIS.heart.name, 0.1*100, 1, 1, beam_set_index = index)
    for i in range(len(ptv)):
      if SSF.has_roi_with_shape(ss, ptv[i]):
        OF.min_dose_robust(ss, plan, ptv[i], 0.95*total_dose*100, 1000)
        OF.max_dose_robust(ss, plan, ptv[i], 1.05*total_dose*100, 3000)
  if technique_name == '3D-CRT': # Hybrid VMAT
    if region_code in RC.breast_tang_r_codes: # Hybrid VMAT Breast tangential RIGHT
      OF.uniform_dose(ss, plan, ROIS.ctv_r.name, total_dose*100, 100, beam_set_index = 1)
      OF.min_dose(ss, plan, ROIS.ptv_pc_r.name, 38.5*100, 3000, beam_set_index = 1)
      OF.fall_off(ss, plan, ROIS.body.name, total_dose*100, 20*100, 1, 1, beam_set_index = 1)
      OF.max_dose(ss, plan, ROIS.body.name,41.5*100, 30000, beam_set_index = 1)
      OF.max_eud(ss, plan, contralateral_breast, 0.5*100, 1, 1, beam_set_index = 1)
      OF.max_eud(ss, plan, ipsilateral_lung, 4*100, 1, 1, beam_set_index = 1)
      OF.max_eud(ss, plan, contralateral_lung, 0.5*100, 1, 1, beam_set_index = 1)
      OF.max_eud(ss, plan, ROIS.heart.name, 1*100, 1, 1, beam_set_index = 1)
    elif region_code in RC.breast_tang_l_codes: # Hybrid VMAT Breast tangential LEFT
      OF.uniform_dose(ss, plan, ROIS.ctv_l.name, total_dose*100, 100, beam_set_index = 1)
      OF.min_dose(ss, plan, ROIS.ptv_pc_l.name, 38.5*100, 3000, beam_set_index = 1)
      OF.fall_off(ss, plan, ROIS.body.name, total_dose*100, 20*100, 1, 1, beam_set_index = 1)
      OF.max_dose(ss, plan, ROIS.body.name,41.5*100, 30000, beam_set_index = 1)
      OF.max_eud(ss, plan, contralateral_breast, 0.5*100, 1, 1, beam_set_index = 1)
      OF.max_eud(ss, plan, ipsilateral_lung, 4*100, 1, 1, beam_set_index = 1)
      OF.max_eud(ss, plan, contralateral_lung, 0.5*100, 1, 1, beam_set_index = 1)
      OF.max_eud(ss, plan, ROIS.heart.name, 1.6*100, 1, 1, beam_set_index = 1) 
    elif region_code in RC.breast_reg_r_codes: # Hybrid VMAT Breast regional RIGHT
      OF.uniform_dose(ss, plan, ROIS.ctv_r.name, total_dose*100, 30, beam_set_index = 1)
      OF.uniform_dose(ss, plan, ROIS.ctv_n_r.name, total_dose*100, 30, beam_set_index = 1)
      OF.min_dose(ss, plan, ROIS.x_ptv_cran.name, 38.4*100, 1000, beam_set_index = 1)
      OF.min_dose(ss, plan, ROIS.ptv_pc_r.name, 38.4*100, 1000, beam_set_index = 1)
      OF.min_dose(ss, plan, ROIS.ptv_nc_r.name, 38.4*100, 1000, beam_set_index = 1)
      OF.fall_off(ss, plan, ROIS.x_ptv_cran.name, total_dose*100, 38.05*100, 1, 10, beam_set_index = 1)
      OF.fall_off(ss, plan, ROIS.external.name, total_dose*100, 30*100, 2, 1, beam_set_index = 1)
      OF.max_dose(ss, plan, ROIS.external.name, 42*100, 50000, beam_set_index = 1)
      OF.max_eud(ss, plan, ROIS.heart.name, 1.8*100, 1, 5, beam_set_index = 1)
      OF.max_dvh(ss, plan, ipsilateral_lung, 18*100, 20, 5, beam_set_index = 1)
      OF.max_dvh(ss, plan, ipsilateral_lung, 5*100, 45, 5, beam_set_index = 1)
      OF.max_eud(ss, plan, ipsilateral_lung, 10*100, 1, 1, beam_set_index = 1)
      OF.max_eud(ss, plan, contralateral_lung, 0.5*100, 1, 1, beam_set_index = 1)
      OF.max_dvh(ss, plan, contralateral_lung, 5*100, 1, 5, beam_set_index = 1)
      OF.max_eud(ss, plan, contralateral_breast, 0.8*100, 1, 1, beam_set_index = 1)
      OF.max_eud(ss, plan, ipsilateral_humeral , 15*100, 1, 10, beam_set_index = 1)
    elif region_code in RC.breast_reg_l_codes: # Hybrid VMAT Breast regional LEFT
      OF.uniform_dose(ss, plan, ROIS.ctv_l.name, total_dose*100, 30, beam_set_index = 1)
      OF.uniform_dose(ss, plan, ROIS.ctv_n_l.name, total_dose*100, 30, beam_set_index = 1)
      OF.min_dose(ss, plan, ROIS.x_ptv_cran.name, 38.4*100, 1000, beam_set_index = 1)
      OF.min_dose(ss, plan, ROIS.ptv_pc_l.name, 38.4*100, 1000, beam_set_index = 1)
      OF.min_dose(ss, plan, ROIS.ptv_nc_l.name, 38.4*100, 1000, beam_set_index = 1)
      OF.fall_off(ss, plan, ROIS.x_ptv_cran.name, total_dose*100, 38.05*100, 1, 10, beam_set_index = 1)
      OF.fall_off(ss, plan, ROIS.external.name, total_dose*100, 30*100, 2, 1, beam_set_index = 1)
      OF.max_dose(ss, plan, ROIS.external.name, 42*100, 50000, beam_set_index = 1)
      OF.max_eud(ss, plan, ROIS.heart.name, 1.8*100, 1, 5, beam_set_index = 1)
      OF.max_dvh(ss, plan, ipsilateral_lung, 18*100, 20, 5, beam_set_index = 1)
      OF.max_dvh(ss, plan, ipsilateral_lung, 5*100, 45, 5, beam_set_index = 1)
      OF.max_eud(ss, plan, ipsilateral_lung, 10*100, 1, 1, beam_set_index = 1)
      OF.max_eud(ss, plan, contralateral_lung, 0.5*100, 1, 1, beam_set_index = 1)
      OF.max_dvh(ss, plan, contralateral_lung, 5*100, 1, 5, beam_set_index = 1)
      OF.max_eud(ss, plan, contralateral_breast, 0.8*100, 1, 1, beam_set_index = 1)
      OF.max_eud(ss, plan, ipsilateral_humeral , 15*100, 1, 10, beam_set_index = 1)       
      if SSF.has_roi_with_shape(ss, ROIS.x_ctv_n_ring.name): #kanskje oppdatere dette til vår xPTV_DFO?
        OF.fall_off(ss, plan, ROIS.x_ctv_n_ring.name, total_dose*100, 30*100, 2, 20, beam_set_index = 1)
      elif SSF.has_roi_with_shape(ss, "xCTVn_L2-L4_Ring"):
        OF.fall_off(ss, plan, "xCTVn_L2-L4_Ring", total_dose*100, 30*100, 2, 20, beam_set_index = 1)
      OF.fall_off(ss, plan, ROIS.esophagus.name, 40*100, 10*100, 1, 10, beam_set_index = 1)
      OF.fall_off(ss, plan, ROIS.thyroid.name, 40*100, 10*100, 1, 10, beam_set_index = 1)
      OF.fall_off(ss, plan, ROIS.trachea.name, 40*100, 10*100, 1, 10, beam_set_index = 1)
  elif technique_name == 'VMAT' and region_code not in RC.breast_partial_codes: # VMAT except boost
    # VMAT automatic optimization
    # Common for all VMAT breast automatic (except boost)
    ctv = [ROIS.ctv_p.name, ROIS.ctv_n.name, ROIS.ctv_l.name, ROIS.ctv_r.name, ROIS.ctv_n_l.name, ROIS.ctv_n_r.name, ROIS.ctv_imn.name,  ROIS.ctv_imn_r.name,  ROIS.ctv_imn_l.name ]
    ptv = [ROIS.ptv_pc.name, ROIS.ptv_nc.name, ROIS.ptv_pc_l.name, ROIS.ptv_pc_r.name, ROIS.ptv_nc_l.name, ROIS.ptv_nc_r.name,ROIS.ptv_n_imn.name,ROIS.ptv_n_imn_r.name,ROIS.ptv_n_imn_l.name]
    for i in range(len(ctv)):
      if SSF.has_roi_with_shape(ss, ctv[i]):
        OF.uniform_dose(ss, plan, ctv[i], total_dose*100, 10)
    for i in range(len(ctv)):
      if SSF.has_roi_with_shape(ss, ctv[i]):
        OF.min_dose(ss, plan, ctv[i], 38.5*100, 300)
    for i in range(len(ptv)):
      if SSF.has_roi_with_shape(ss, ptv[i]):
        OF.min_dose(ss, plan, ptv[i], 38.2*100, 300)
    OF.max_dose(ss, plan, ROIS.body.name, 42.5*100, 50000)
    OF.fall_off(ss, plan, ROIS.body.name, 40*100, 20*100, 1, 1)
    OF.max_eud(ss, plan, ROIS.heart.name, 1*100, 1, 10)
    if region_code in RC.breast_l_codes:
      OF.max_eud(ss, plan, ROIS.a_lad.name, 7*100, 1, 10)
    if SSF.has_roi_with_shape(ss, ROIS.ctv_r.name) and SSF.has_roi_with_shape(ss, ROIS.ctv_l.name): # VMAT Breast bilateral automatic
      OF.max_eud(ss, plan, ROIS.lung_l.name, 5*100, 1, 20)
      OF.max_eud(ss, plan, ROIS.lung_r.name, 5*100, 1, 20)
      OF.max_dvh(ss, plan, ROIS.lung_l.name, 2*100, 45, 10)
      OF.max_dvh(ss, plan, ROIS.lung_r.name, 2*100, 45, 10)
      if region_code in RC.breast_tang_codes: # VMAT tangential breast bilateral automatic
        OF.fall_off(ss, plan, ROIS.sternum_box.name, 38*100, 30*100, 1, 100)
      if region_code in RC.breast_reg_codes: # VMAT regional breast bilateral automatic
        if SSF.has_roi_with_shape(ss, ROIS.ctv_n_l.name):
          OF.max_dose(ss, plan, ROIS.humeral_l.name, 30*100, 2)
          OF.max_eud(ss, plan, ROIS.humeral_l.name, 4*100, 1, 2)
        if SSF.has_roi_with_shape(ss, ROIS.ctv_n_r.name):
          OF.max_dose(ss, plan, ROIS.humeral_r.name, 30*100, 2)
          OF.max_eud(ss, plan, ROIS.humeral_r.name, 4*100, 1, 2)  
    else: # VMAT Breast one sided automatic
      if SSF.has_roi_with_shape(ss, ROIS.ctv_imn_r.name) or SSF.has_roi_with_shape(ss, ROIS.ctv_imn_l.name): # VMAT breast with IMN automatic
        OF.max_eud(ss, plan, ipsilateral_lung, 6*100, 1, 20)
      else: #VMAT breast reginal without IMN automatic
        OF.max_eud(ss, plan, ipsilateral_lung, 5*100, 1, 20)
      OF.max_dvh(ss, plan, ipsilateral_lung, 2*100, 35, 10)
      OF.max_eud(ss, plan, contralateral_lung, 1*100, 1, 10)
      OF.max_eud(ss, plan, contralateral_breast, 1*100, 1, 10)
      if region_code in RC.breast_reg_codes: # VMAT Breast regional not bilateral automatic
        OF.max_eud(ss, plan, ipsilateral_humeral, 4*100, 1, 2)
        OF.max_dose(ss, plan, ipsilateral_humeral, 30*100, 2)
    if region_code in RC.breast_reg_codes: # VMAT Breast regional automatic
      OF.max_eud(ss, plan, ROIS.esophagus.name, 2*100, 1, 2)
      OF.max_eud(ss, plan, ROIS.trachea.name, 3*100, 1, 2)
      OF.max_eud(ss, plan, ROIS.thyroid.name, 4*100, 1, 2)
      if SSF.has_roi_with_shape(ss, ROIS.x_ctv_n_ring.name):
        OF.fall_off(ss, plan, ROIS.x_ctv_n_ring.name, 42*100, 20*100, 1.5, 100)
      elif SSF.has_roi_with_shape(ss, "xCTVn_L2-L4_Ring"):
        OF.fall_off(ss, plan, "xCTVn_L2-L4_Ring", 42*100, 20*100, 1.5, 100)
      OF.fall_off(ss, plan, ROIS.sternum_box.name, 38*100, 25*100, 1, 100)
    ptv = [ROIS.ptv_pc.name, ROIS.ptv_nc.name, ROIS.ptv_pc_l.name, ROIS.ptv_pc_r.name, ROIS.ptv_nc_l.name, ROIS.ptv_nc_r.name]
    for i in range(len(ptv)):
      if SSF.has_roi_with_shape(ss, ptv[i]):
        OF.min_dose_robust(ss, plan, ptv[i], 37.5*100, 1000)
        OF.max_dose_robust(ss, plan, ptv[i], 42*100, 5000)