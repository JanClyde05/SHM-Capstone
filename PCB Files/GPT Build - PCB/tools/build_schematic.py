"""Reproduce SHM Node R2 schematic from installed KiCad 10 symbols.

Only writes this project's generated schematic and circuit_spec.json.
Electrical choices: docs/RESEARCH_LEDGER.md and docs/ELECTRICAL_DECISIONS.md.
No hand edits to generated schematic: change this source and regenerate.
"""
from pathlib import Path
import re, json, uuid, copy, math

ROOT = Path(__file__).resolve().parents[1]
LIB = Path('C:/Program Files/KiCad/10.0/share/kicad/symbols')
def generate_local_module_footprint():
    """Keep manufacturer geometry; move overhanging antenna artwork off silkscreen."""
    import pcbnew
    source=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints/RF_Module.pretty')
    fp=pcbnew.FootprintLoad(str(source),'ESP32-S3-WROOM-1')
    assert fp is not None
    def pads(f):
        return sorted((p.GetNumber(),p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y,p.GetShape()) for p in f.Pads())
    original=pads(fp); moved=0
    for graphic in fp.GraphicalItems():
        if graphic.GetLayer()==pcbnew.F_SilkS and pcbnew.ToMM(graphic.GetBoundingBox().GetTop()) < -7.8:
            graphic.SetLayer(pcbnew.F_Fab);moved+=1
        elif graphic.GetLayer()==pcbnew.F_SilkS and graphic.GetShape()==pcbnew.SHAPE_T_POLY:
            # Compact-reference top-edge clearance; only pin-1 artwork moves.
            graphic.Move(pcbnew.VECTOR2I(0,pcbnew.FromMM(.1)))
    name='ESP32-S3-WROOM-1_Overhang'
    fp.SetFPID(pcbnew.LIB_ID('SHM_Local',name))
    fp.SetLibDescription('KiCad ESP32-S3-WROOM-1: identical pads/courtyard; antenna artwork moved from F.SilkS to F.Fab where antenna overhangs the board.')
    target=ROOT/'design/SHM_Local.pretty';target.mkdir(parents=True,exist_ok=True)
    pcbnew.FootprintSave(str(target),fp)
    saved=pcbnew.FootprintLoad(str(target),name)
    assert pads(saved)==original, 'Local footprint pad geometry changed unexpectedly'
    print(f'Local ESP32 footprint: {moved} antenna graphics moved to F.Fab, pad geometry identical')
generate_local_module_footprint()
NAMESPACE = uuid.UUID('b60ece5a-fec4-4555-8bcc-a6eb6592c1e2')
def uid(s): return str(uuid.uuid5(NAMESPACE, s))
def q(s): return json.dumps(str(s))
def num(v): return ('%.4f' % v).rstrip('0').rstrip('.')
def parse(t):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+', t)
    def read(i):
        if tokens[i] != '(': return tokens[i], i+1
        out=[]; i+=1
        while tokens[i] != ')':
            item,i=read(i); out.append(item)
        return out,i+1
    return read(0)[0]
def emit(x): return '('+' '.join(emit(v) if isinstance(v,list) else v for v in x)+')'
def child(x,key): return next((v for v in x if isinstance(v,list) and v[0]==key),None)
def children(x,key): return [v for v in x if isinstance(v,list) and v[0]==key]
def val(x): return json.loads(x) if x.startswith('"') else x
def load(lib_id):
    lib,name=lib_id.split(':'); tree=parse((LIB/(lib+'.kicad_sym')).read_text(encoding='utf-8'))
    symbols={val(x[1]):x for x in children(tree,'symbol')}
    def flatten(n):
        own=copy.deepcopy(symbols[n]); ext=child(own,'extends')
        if not ext: return own
        base=flatten(val(ext[1])); old=val(base[1]); base[1]=q(n)
        ownprops={v[1]:v for v in children(own,'property')}
        base=[v for v in base if not(isinstance(v,list) and v[0]=='property' and v[1] in ownprops)]
        base+=list(ownprops.values())
        for v in children(base,'symbol'): v[1]=q(val(v[1]).replace(old+'_',n+'_',1))
        return base
    result=flatten(name); result[1]=q(lib_id)
    return result

parts=[]; items=[]; caches={}; counter=0
SCH_ID=uid('schematic')
def effects(size=1.0, justify='', hidden=False):
    return '(effects (font (size %s %s))%s%s)'%(size,size,(' (justify '+justify+')') if justify else '', ' (hide yes)' if hidden else '')
def wire(a,b):
    global counter
    counter+=1;items.append('(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid %s))'%(*map(num,a),*map(num,b),q(uid('wire'+str(counter)))))
def label(text,p,angle=0,justify='left bottom'):
    global counter
    counter+=1;items.append('(label %s (at %s %s %s) %s (uuid %s))'%(q(text),*map(num,p),angle,effects(.95,justify),q(uid('label'+str(counter)))))
def note(text,x,y,size=1.1):
    global counter
    counter+=1;items.append('(text %s (at %s %s 0) %s (uuid %s))'%(q(text),num(x),num(y),effects(size,'left top'),q(uid('text'+str(counter)))))

def power_at(net,x,y):
    global counter
    counter+=1; lib_id='power:'+net
    if lib_id not in caches: caches[lib_id]=load(lib_id)
    ref='#PWR'+str(counter); vpos=y+3.81 if net=='GND' else y-3.81
    props='(property "Reference" %s (at %s %s 0) %s) (property "Value" %s (at %s %s 0) %s)'%(q(ref),num(x),num(y),effects(1,hidden=True),q(net),num(x),num(vpos),effects(.95,hidden=net=='GND'))
    items.append('(symbol (lib_id %s)(at %s %s 0)(unit 1)(in_bom no)(on_board no)(dnp no)(uuid %s) %s (pin "1"(uuid %s))(instances(project "SHM_Node_R2"(path %s(reference %s)(unit 1)))))'%(q(lib_id),num(x),num(y),q(uid(ref)),props,q(uid(ref+'pin')),q('/'+SCH_ID),q(ref)))
def box(x1,y1,x2,y2,title):
    global counter
    counter+=1;items.append('(rectangle (start %s %s) (end %s %s) (stroke (width .254) (type default)) (fill (type none)) (uuid %s))'%(*map(num,[x1,y1,x2,y2]),q(uid('box'+str(counter)))))
    note(title,x1+2.54,y1+2.54,1.4)
def instance(lib_id,ref,value,fp,pins,x,y,angle=0,props=None):
    if lib_id not in caches: caches[lib_id]=load(lib_id)
    sym=caches[lib_id]; pinlist=[]
    for unit in children(sym,'symbol'):
        for pin in children(unit,'pin'):
            at=child(pin,'at'); pinlist.append({'number':val(child(pin,'number')[1]),'name':val(child(pin,'name')[1]),'x':float(at[1]),'y':float(at[2]),'angle':float(at[3])})
    c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle))
    def tr(px,py): return (round(x+px*c-py*s,4),round(y-px*s-py*c,4))
    pstr=[]; seen=set()
    for pin in pinlist:
        pn=pin['number'];pos=tr(pin['x'],pin['y']);key=(pos,pins.get(pn))
        pstr.append('(pin %s (uuid %s))'%(q(pn),q(uid(ref+'pin'+pn))))
        if key in seen: continue
        seen.add(key)
        if pn not in pins:
            items.append('(no_connect (at %s %s) (uuid %s))'%(*map(num,pos),q(uid(ref+'nc'+pn))));continue
        # Pins point INTO symbols. Stub goes opposite the local pin direction.
        a=math.radians(pin['angle']+angle)
        end=(round(pos[0]-5.08*math.cos(a),4),round(pos[1]+5.08*math.sin(a),4))
        wire(pos,end)
        if abs(end[1]-pos[1])<.01:
            left=end[0]<pos[0]; label(pins[pn],end,0,'right bottom' if left else 'left bottom')
        elif lib_id.startswith('Connector:TestPoint'): label(pins[pn],end,0,'left bottom')
        elif pins[pn] in ['+3V3','GND']: power_at(pins[pn],*end)
        else: label(pins[pn],end,0,'left bottom')
    rx,ry=x,y-5.08; vx,vy=x,y-2.54
    if lib_id.startswith('RF_Module:'): rx,ry=x-30.48,y-34.29;vx,vy=x-30.48,y-31.75
    elif lib_id.startswith('Sensor_Motion:'):rx,ry=x-19.05,y-25.4;vx,vy=x-19.05,y-22.86
    elif lib_id.startswith('Connector:USB'):rx,ry=x,y-25.4;vx,vy=x,y-22.86
    elif lib_id in ['Device:R','Device:C','Device:Polyfuse']:
        if angle==0:rx,ry=x+3.81,y-1.27;vx,vy=x+3.81,y+1.27
    elif lib_id.startswith('Connector:TestPoint'):rx,ry=x+3.81,y-2.54;vx,vy=x+3.81,y
    elif lib_id=='Connector_Generic:Conn_01x03':rx,ry=x,y-8.89;vx,vy=x,y-6.35
    elif lib_id=='Regulator_Linear:AP7361C-33E':rx,ry=x,y-10.16;vx,vy=x,y-7.62
    elif lib_id=='Power_Protection:USBLC6-2SC6':rx,ry=x-16.51,y-12.7;vx,vy=x-16.51,y-10.16
    elif lib_id=='power:PWR_FLAG':rx,ry=x,y-8.89;vx,vy=x,y-6.35
    # Name and value fields have deliberate positions, independent of KiCad autoplacement.
    field_justify='left' if (angle==0 and (lib_id in ['Device:R','Device:C','Device:Polyfuse'] or lib_id.startswith('Connector:TestPoint'))) else ''
    prop='(property "Reference" %s (at %s %s 0) %s) (property "Value" %s (at %s %s 0) %s) (property "Footprint" %s (at %s %s 0) %s)'%(q(ref),num(rx),num(ry),effects(1.05,field_justify),q(value),num(vx),num(vy),effects(1.0,field_justify,hidden=lib_id.startswith('Connector:TestPoint')),q(fp),num(x),num(y),effects(1.0,hidden=True))
    if props:
        for k,v in props.items():prop+=' (property %s %s (at %s %s 0) %s)'%(q(k),q(v),num(x),num(y),effects(1.0,hidden=True))
    if angle==90:
        prop=prop.replace('(at %s %s 0)'%(num(rx),num(ry)),'(at %s %s 90)'%(num(rx),num(ry))).replace('(at %s %s 0)'%(num(vx),num(vy)),'(at %s %s 90)'%(num(vx),num(vy)))
    instance_text='(symbol (lib_id %s) (at %s %s %s) (unit 1) (in_bom %s) (on_board %s) (dnp no) (uuid %s) %s %s (instances (project "SHM_Node_R2" (path %s (reference %s) (unit 1)))))'%(q(lib_id),num(x),num(y),angle,'no' if ref.startswith('#') else 'yes','no' if ref.startswith('#') else 'yes',q(uid(ref)),prop,' '.join(pstr),q('/'+SCH_ID),q(ref))
    items.append(instance_text)
    if not ref.startswith('#'):parts.append({'ref':ref,'value':value,'lib_id':lib_id,'footprint':fp,'pins':pins,'uuid':uid(ref),'schematic_mm':[x,y],'properties':props or {}})

R='Resistor_SMD:R_0603_1608Metric';C='Capacitor_SMD:C_0603_1608Metric';CB='Capacitor_SMD:C_0805_2012Metric'
def resistor(ref,value,a,b,x,y,angle=0): instance('Device:R',ref,value,R,{'1':a,'2':b},x,y,angle)
def capacitor(ref,value,a,x,y,bulk=False):instance('Device:C',ref,value,CB if bulk else C,{'1':a,'2':'GND'},x,y,props={'Voltage':'50V' if value=='2.2nF' else '16V' if bulk else '25V','Dielectric':'X7R','Tolerance':'10% or better'})

# Three complete XYZ sensors; one bus with two fixed addresses, second bus with one.
for i,x in enumerate([76.2,209.55,342.9],1):
    left=x-63.5;box(left,15.24,left+127,124.46,f'IMU {i} / COMPLETE X-Y-Z / BUS {0 if i<3 else 1} / 0x{104 if i!=2 else 105:02X}')
    nets={'1':'GND','8':'+3V3','9':'+3V3' if i==2 else 'GND','10':f'IMU{i}_REGOUT','11':'GND','12':f'IMU{i}_INT','13':'+3V3','18':'GND','20':f'IMU{i}_CPOUT','23':f'I2C{0 if i<3 else 1}_SCL','24':f'I2C{0 if i<3 else 1}_SDA'}
    instance('Sensor_Motion:MPU-6050',f'U{i+1}','MPU-6050','SHM_Local:MPU6050_QFN24_NoCenterPad',nets,x,57.15)
    for j,(value,net) in enumerate([('100nF','+3V3'),('10nF','+3V3'),('100nF',f'IMU{i}_REGOUT'),('2.2nF',f'IMU{i}_CPOUT')]):
        ref=f'C{6+(i-1)*4+j}';cx=left+12.7+j*29.21
        capacitor(ref,value,net,cx,102.87)
        if j==3: parts[-1]['properties']['Voltage']='50V'
        note(['VDD pin 13','VLOGIC pin 8','REGOUT pin 10','CPOUT pin 20'][j],cx-5.08,115.57,.95)
    note('No center paste/pad. Reserved pins NC. All three packages share board axes.',left+2.54,84.5,.95)

box(12.7,129.54,139.7,259.08,'USB-C / 5V INPUT / 3.3V REGULATOR')
instance('Connector:USB_C_Receptacle_USB2.0_16P','J1','USB4105-GF-A','Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal',{'A1':'GND','A4':'VBUS_USB','A5':'CC1','A6':'USB_DP','A7':'USB_DM','A9':'VBUS_USB','A12':'GND','B1':'GND','B4':'VBUS_USB','B5':'CC2','B6':'USB_DP','B7':'USB_DM','B9':'VBUS_USB','B12':'GND','SH':'GND'},35.56,165.1)
resistor('R1','5.1k 1%','CC1','GND',88.9,158.75)
resistor('R2','5.1k 1%','CC2','GND',115.57,158.75)
instance('Power_Protection:USBLC6-2SC6','U6','USBLC6-2SC6','Package_TO_SOT_SMD:SOT-23-6',{'1':'USB_DM','2':'GND','3':'USB_DP','4':'USB_DP','5':'VBUS_USB','6':'USB_DM'},109.22,194.31)
instance('Device:Polyfuse','F1','0.75A HOLD','Fuse:Fuse_1206_3216Metric',{'1':'VBUS_USB','2':'+5V_FUSED'},46.99,207.01,90,{'MPN':'1206L075/16WR','Datasheet':'https://www.littelfuse.com/assetdocs/littelfuse-ptc-1206l-datasheet?assetguid=2b6a1515-d4ee-4c83-8bd4-152b4901b8f5'})
instance('Regulator_Linear:AP7361C-33E','U5','AP7361C-33E-13','Package_TO_SOT_SMD:SOT-223-3_TabPin2',{'1':'+5V_FUSED','2':'GND','3':'+3V3'},46.99,238.76,props={'Datasheet':'https://www.diodes.com/datasheet/download/AP7361C.pdf'})
capacitor('C1','4.7uF','+5V_FUSED',92.71,238.76,True)
capacitor('C2','10uF','+3V3',119.38,238.76,True)
note('U5: pin 1 IN / pin 2 + tab GND / pin 3 OUT. Qualify thermal rise.',15.24,256.54,.95)

box(144.78,129.54,271.78,259.08,'ESP32-S3-WROOM-1-N16R8 / NATIVE USB')
esp={'1':'GND','2':'+3V3','3':'EN','4':'IMU1_INT','5':'IMU2_INT','6':'IMU3_INT','12':'I2C0_SDA','13':'USB_DM_MCU','14':'USB_DP_MCU','17':'I2C0_SCL','18':'I2C1_SDA','19':'I2C1_SCL','27':'BOOT','36':'UART_RX','37':'UART_TX','40':'GND','41':'GND'}
instance('RF_Module:ESP32-S3-WROOM-1','U1','ESP32-S3-WROOM-1-N16R8','SHM_Local:ESP32-S3-WROOM-1_Overhang',esp,208.28,180.34)
capacitor('C3','10uF','+3V3',163.83,237.49,True)
capacitor('C4','100nF','+3V3',193.04,237.49)
instance('Connector_Generic:Conn_01x03','J2','UART DEBUG (3V3 LOGIC)','Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',{'1':'GND','2':'UART_TX','3':'UART_RX'},247.65,238.76)
note('GPIO35/36/37 unused: reserved for module PSRAM.',147.32,219.71,.95)
note('GPIO19 = USB D-; GPIO20 = USB D+. Header TX/RX at 3.3V.',147.32,251.46,.95)

box(276.86,129.54,403.86,250.19,'RESET / BOOT / I2C PULLUPS / USB DAMPING')
resistor('R5','10k','+3V3','EN',289.56,154.94)
capacitor('C5','1uF','EN',326.39,154.94)
instance('Switch:SW_Push','SW1','RESET','Button_Switch_SMD:SW_SPST_TL3342',{'1':'EN','2':'GND'},378.46,154.94)
resistor('R6','10k','+3V3','BOOT',289.56,185.42)
instance('Switch:SW_Push','SW2','BOOT','Button_Switch_SMD:SW_SPST_TL3342',{'1':'BOOT','2':'GND'},378.46,185.42)
for j,net in enumerate(['I2C0_SDA','I2C0_SCL','I2C1_SDA','I2C1_SCL']):resistor(f'R{7+j}','2.2k','+3V3',net,289.56+j*30.48,215.9)
resistor('R3','22R','USB_DM','USB_DM_MCU',304.8,243.84,90)
resistor('R4','22R','USB_DP','USB_DP_MCU',369.57,243.84,90)

box(12.7,261.62,297.18,284.48,'TEST POINTS / SIGNAL AND SUPPLY ACCESS')
for i,net in enumerate(['+3V3','GND','I2C0_SDA','I2C0_SCL','I2C1_SDA','I2C1_SCL','IMU1_INT','IMU2_INT','IMU3_INT','UART_TX','UART_RX'],1):
    instance('Connector:TestPoint',f'TP{i}',net,'TestPoint:TestPoint_Pad_D1.0mm',{'1':net},25.4+(i-1)*25.4,275.59)

# PWR_FLAG reflects externally supplied USB VBUS/GND and power passed through fuse.
for i,(net,x) in enumerate([('VBUS_USB',85.09),('GND',106.68),('+5V_FUSED',128.27)],1):
    instance('power:PWR_FLAG',f'#FLG0{i}','PWR_FLAG','',{'1':net},x,220.98)

header=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{SCH_ID}") (paper "A3") (title_block (title "SHM Frequency Acquisition Node") (date "2026-10-25") (rev "R2 prototype") (company "Jan Clyde T. Talosig") (comment 1 "ESP32-S3-WROOM-1-N16R8 / three complete triaxial MPU-6050 ICs"))'
text=header+'\n(lib_symbols\n'+'\n'.join(emit(v) for v in caches.values())+'\n)\n'+'\n'.join(items)+'\n(embedded_fonts no))\n'
(ROOT/'design').mkdir(exist_ok=True)
(ROOT/'design/SHM_Node_R2.kicad_sch').write_text(text,encoding='utf-8')
spec={'schema':1,'project':'SHM_Node_R2','revision':'R2 prototype','schematic_uuid':SCH_ID,'components':parts,'notes':['Pin keys are PACKAGE pin numbers, not GPIO numbers.','No center copper/paste pad on MPU-6050 footprint.','USBLC6 pins 1/6 share DM; pins 3/4 share DP. Route through protection footprint.','C1 4.7uF input, C2 10uF output; qualify effective capacitance, inrush and thermal rise.']}
(ROOT/'design/circuit_spec.json').write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
print(f'Wrote schematic and circuit_spec.json: {len(parts)} physical components')
