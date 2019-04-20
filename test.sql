

SELECT loc.pid,loc.name,loc.address, loc.city, loc.state, loc.phone, paym.cost,comp.score
FROM (SELECT hospital.providerID as pid, hospitalName as name, hospital.address as address,city.cityName as city, city.stateName as state, hospital.phone as phone
		FROM hospital, city
		WHERE hospital.zip = city.zip) as loc, 
	(SELECT paymentAmount as cost,providerID
		FROM hospital_payment
		WHERE paymentID like 'PAYM_%%_AMI') as paym,
	(SELECT compScore as score,providerID
		FROM hospital_comp
		WHERE measureID like 'MORT_%%_AMI') as comp
WHERE loc.pid = paym.providerID
AND loc.pid = comp.providerID;


SELECT loc.pid,loc.name,loc.address, loc.city, loc.state, loc.phone, paym.cost,comp.score 
FROM (SELECT hospital.providerID as pid, hospitalName as name, hospital.address as address,city.cityName as city, city.stateName as state, hospital.phone as phone 
	FROM hospital,city) as loc,
	(SELECT paymentAmount as cost,providerID 
		FROM hospital_payment 
		WHERE paymentID like 'PAYM_%%_AMI') as paym,
	(SELECT compScore as score,providerID 
		FROM hospital_comp 
		WHERE measureID like 'MORT_%%_AMI') as comp 
WHERE loc.pid = paym.providerId 
AND loc.pid = comp.providerID 
ORDER BY loc.name;

SELECT loc.name,loc.city,hospital_comp.measureID,hospital_comp.compScore
FROM
(SELECT hospital.providerID as pid, hospitalName as name, 
	hospital.address as address,city.cityName as city, city.stateName as state, hospital.phone as phone 
	FROM hospital, city WHERE hospital.zip = '12180' AND city.zip = '12180') as loc, hospital_comp
WHERE loc.pid = hospital_comp.providerID;

SELECT loc.name,loc.city,hospital_payment.paymentID,hospital_payment.paymentAmount
FROM
(SELECT hospital.providerID as pid, hospitalName as name, 
	hospital.address as address,city.cityName as city, city.stateName as state, hospital.phone as phone 
	FROM hospital, city WHERE hospital.zip = '12180' AND city.zip = '12180') as loc, hospital_payment
WHERE loc.pid = hospital_payment.providerID;

