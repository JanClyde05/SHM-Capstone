"""Deterministic hardware calculations, with explicitly hypothetical inputs.
No result here is a measurement or a full worst-case tolerance/thermal analysis.
Equation IDs link to docs/ENGINEERING_AUDIT_20261029.md.
"""
from pathlib import Path
import datetime, hashlib, json, math
ROOT=Path(__file__).resolve().parents[1]
spec=ROOT/'design/circuit_spec.json'
s=json.loads(spec.read_text()); parts={c['ref']:c for c in s['components']}
assert parts['U5']['value']=='AP7361C-33E-13'
assert all(parts[r]['value']=='2.2k' for r in ['R7','R8','R9','R10'])
assert parts['R5']['value']=='10k' and parts['C5']['value']=='1uF'
vin,vout=5.0,3.3
thermal=[]
for amps in [.3,.5,1.0]:
    # EQ-P01: power balance, neglecting unspecified loaded ground current.
    watts=(vin-vout)*amps
    # EQ-P02: steady-state lumped thermal model; theta is NOT this board's value.
    thermal.append({'load_A_hypothetical':amps,'dissipation_W_excluding_ground_current':round(watts,6),'rise_C_if_theta_110_C_per_W':round(watts*110,6),
                    'Tj_C_if_ambient_25C_and_theta_110':round(25+watts*110,6),'Tj_C_if_ambient_50C_and_theta_110':round(50+watts*110,6)})
rp=2200.;tr=300e-9
maths={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'spec_sha256':hashlib.sha256(spec.read_bytes()).hexdigest(),
 'EQ_P01_P02':{'Vin_V_assumed':vin,'Vout_V_nominal':vout,'theta_C_per_W_reference_test_board_only':110,'cases':thermal,'limits':'Load/ambient are illustrative, not measured or selected limits. Ignd term excluded. Extrapolation above thermal shutdown is not a physically sustainable junction temperature.'},
 # EQ-I01 comes from the capacitor charge law between 30% and 70%.
 'EQ_I01_I02':{'rise_coefficient_exact':math.log(.7/.3),'rise_coefficient_source_rounded':.8473,'Rp_ohm_nominal':rp,'tr_s_max_Fast_mode':tr,
  'Cb_pF_max_nominal':tr/(.8473*rp)*1e12,'Cb_pF_max_if_Rp_plus1pct':tr/(.8473*rp*1.01)*1e12,'tr_ns_if_Cb_100pF':.8473*rp*100e-12*1e9,
  'limits':'1% resistor tolerance is only proposed in BOM; no MPN selected. Actual capacitance includes ICs, PCB, pad, fixture and probe.'},
 # EQ-I03 is Ohm's law, using source stated IOL and VOL for the MPU primary bus.
 'EQ_I03':{'Vdd_V_nominal':3.3,'Vol_V':.4,'Iol_A_source_condition':.003,'Rp_min_ohm_at_3_3V':(3.3-.4)/.003,'Rp_min_ohm_at_3_46V':(3.46-.4)/.003,
  'sink_mA_at_3_3V_and_0_4V':(3.3-.4)/rp*1e3,'sink_mA_at_3_46V_and_Rp_minus1pct':(3.46-.4)/(rp*.99)*1e3,'four_lines_low_mA_at_3_3V_Vol0':4*3.3/rp*1e3,
  'limits':'MPU datasheet labels this primary-I2C table Typical; this is not a guaranteed all-temperature bound. ESP GPIO sink capability must also be respected.'},
 # EQ-R01/R02 step-input RC; actual rail ramp and enable threshold are unknown.
 'EQ_R01_R02':{'R_ohm':10000,'C_F':1e-6,'tau_ms':10000*1e-6*1e3,'time_to_75pct_ms_illustrative_threshold':-10000*1e-6*math.log(1-.75)*1e3,
  'limits':'75% is an illustrative threshold for the formula, not an asserted actual EN trip point. Component tolerance, DC bias, leakage and supply ramp excluded.'},
 # EQ-P03 illustrative source-condition subtotal, not additive independent maxima.
 'EQ_P03':{'ESP_documented_peak_condition_mA':355,'three_MPU_typical_gyro_accel_and_logic_mA':3*(3.8+.1),'four_I2C_low_lines_mA':6,'illustrative_subtotal_mA':355+3*(3.8+.1)+6,
  'limits':'Mixed test conditions; excludes other loads, startup, actual PSRAM/flash activity and margin. Not a guaranteed peak, continuous current or measured budget.'},
 'EQ_P04':{'Vout_at_nominal_plus_1pct_V':3.3*1.01,'remaining_to_MPU_3_46V_V':3.46-3.3*1.01,'limits':'1% regulator accuracy applies at specified datasheet conditions; temperature/load/line/ripple/overshoot not bounded by this arithmetic.'},
 'status':'verified arithmetic under stated inputs; actual design operating margin unverified'}
out=ROOT/'reports/engineering_audit/20261029/math.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(maths,indent=2),encoding='utf-8')
print(json.dumps({'output':str(out),'thermal':thermal,'Cmax_pF':maths['EQ_I01_I02']['Cb_pF_max_nominal'],'subtotal_mA':maths['EQ_P03']['illustrative_subtotal_mA']},indent=2))
