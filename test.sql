SELECT hospital.hospitalName, hospital.zip, hospital_comp.measureID, hospital_comp.compScore,hospital_comp.quantity
FROM hospital, hospital_comp
WHERE hospital.providerID = hospital_comp.providerID
AND hospital.zip = '62002'
AND hospital.hospitalName like '%SAINT%';

