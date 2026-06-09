"""
Management command to load initial data for the Medical Wholesale System.
Creates all categories, products, medicines, a sample warehouse, and admin user.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify


User = get_user_model()


EQUIPMENT_CATEGORIES = [
    ('Diagnostic Equipment', 'Equipment for patient diagnosis'),
    ('Surgical Instruments', 'Tools and instruments used in surgery'),
    ('Laboratory Equipment', 'Equipment for laboratory testing and analysis'),
    ('Patient Monitoring', 'Equipment for monitoring patient vital signs'),
    ('Imaging Equipment', 'X-ray, ultrasound and imaging devices'),
    ('Dental Equipment', 'Dental treatment and diagnostic equipment'),
    ('Rehabilitation Equipment', 'Physical therapy and rehabilitation devices'),
    ('Hospital Furniture', 'Hospital beds, trolleys and furniture'),
    ('Personal Protective Equipment', 'PPE for healthcare workers'),
    ('Sterilization Equipment', 'Autoclaves and sterilization devices'),
    ('Ophthalmic Equipment', 'Eye examination and treatment equipment'),
    ('Emergency & Resuscitation', 'Defibrillators, AED and emergency equipment'),
]

MEDICINE_CATEGORIES = [
    ('Essential Medicines', 'Ethiopian Essential Medicine List (NLEM)'),
    ('Analgesics & NSAIDs', 'Pain relievers and anti-inflammatory medicines'),
    ('Antibiotics', 'Antibacterial medicines'),
    ('Antimalarials', 'Medicines for malaria treatment and prevention'),
    ('Antituberculosis', 'TB treatment medicines'),
    ('Antiretrovirals', 'HIV/AIDS treatment medicines'),
    ('Antifungals', 'Antifungal medicines'),
    ('Antiparasitic', 'Antiparasitic medicines'),
    ('Cardiovascular', 'Heart and blood pressure medicines'),
    ('Diabetes Medicines', 'Antidiabetic medicines and insulin'),
    ('Gastrointestinal', 'Digestive system medicines'),
    ('Respiratory', 'Respiratory and asthma medicines'),
    ('Psychiatric & Neurological', 'Mental health and neurological medicines'),
    ('Vitamins & Minerals', 'Nutritional supplements'),
    ('Ophthalmology', 'Eye medicines'),
    ('Dermatology', 'Skin medicines'),
    ('Obstetrics & Gynecology', 'Maternal and reproductive health medicines'),
    ('Anesthesia & Emergency', 'Anaesthetic and emergency medicines'),
    ('IV Fluids & Solutions', 'Intravenous fluids'),
    ('Vaccines', 'Vaccines and immunologicals'),
    ('Disinfectants & Antiseptics', 'Disinfection and antiseptic products'),
]


EQUIPMENT_PRODUCTS = {
    'Diagnostic Equipment': [
        ('Stethoscope', 'piece', False, False),
        ('Blood Pressure Monitor (Digital)', 'piece', False, False),
        ('Pulse Oximeter', 'piece', False, False),
        ('Thermometer Digital', 'piece', False, False),
        ('Glucometer', 'piece', False, False),
        ('Otoscope', 'piece', False, False),
        ('Ophthalmoscope', 'piece', False, False),
        ('ECG Machine (12 Lead)', 'piece', False, False),
        ('Spirometer', 'piece', False, False),
        ('Reflex Hammer', 'piece', False, False),
    ],
    'Surgical Instruments': [
        ('Surgical Scissors (Mayo)', 'piece', False, False),
        ('Surgical Forceps (Kocher)', 'piece', False, False),
        ('Scalpel Handle #3', 'piece', False, False),
        ('Surgical Needle Holder', 'piece', False, False),
        ('Retractor (Langenbeck)', 'piece', False, False),
        ('Artery Clamp', 'piece', False, False),
        ('Tissue Forceps', 'piece', False, False),
        ('Suturing Kit', 'set', False, False),
        ('Surgical Blade Box (100)', 'box', False, False),
    ],
    'Laboratory Equipment': [
        ('Microscope (Binocular)', 'piece', False, False),
        ('Centrifuge (Benchtop)', 'piece', False, False),
        ('Hemoglobin Meter', 'piece', False, False),
        ('Urine Dipstick (50 strips)', 'pack', False, False),
        ('Blood Glucose Test Strips (50)', 'pack', False, False),
        ('Malaria RDT Test Kit', 'piece', False, False),
        ('HIV Test Kit (Determine)', 'piece', False, False),
        ('Pregnancy Test Strip (25)', 'pack', False, False),
        ('Sputum Collection Container', 'piece', False, False),
        ('Laboratory Gloves (100)', 'box', False, False),
    ],
    'Patient Monitoring': [
        ('Multi-Parameter Monitor', 'piece', False, False),
        ('SpO2 Monitor', 'piece', False, False),
        ('Fetal Heart Rate Monitor', 'piece', False, False),
        ('IV Infusion Pump', 'piece', False, False),
        ('Syringe Pump', 'piece', False, False),
        ('Continuous Glucose Monitor', 'piece', False, False),
    ],
    'Imaging Equipment': [
        ('Portable Ultrasound Machine', 'piece', False, False),
        ('Digital X-Ray System', 'piece', False, False),
        ('X-Ray Film (100 sheets)', 'box', False, False),
        ('Ultrasound Gel (1L)', 'bottle', False, False),
    ],
    'Dental Equipment': [
        ('Dental Chair Unit', 'piece', False, False),
        ('Dental Explorer Set', 'set', False, False),
        ('Dental Mirror', 'piece', False, False),
        ('Dental Extraction Forceps', 'piece', False, False),
        ('Dental Syringe (Cartridge)', 'piece', False, False),
        ('Dental Probe', 'piece', False, False),
    ],
    'Rehabilitation Equipment': [
        ('Crutches (Axillary)', 'pair', False, False),
        ('Walking Frame/Zimmer Frame', 'piece', False, False),
        ('Wheelchair (Standard)', 'piece', False, False),
        ('Cervical Collar', 'piece', False, False),
        ('Knee Brace', 'piece', False, False),
        ('TENS Machine', 'piece', False, False),
    ],
    'Hospital Furniture': [
        ('Hospital Bed (Manual)', 'piece', False, False),
        ('Examination Table', 'piece', False, False),
        ('Instrument Trolley', 'piece', False, False),
        ('Medicine Trolley', 'piece', False, False),
        ('IV Stand', 'piece', False, False),
        ('Stretcher Trolley', 'piece', False, False),
        ('Bedside Locker', 'piece', False, False),
    ],
    'Personal Protective Equipment': [
        ('Surgical Mask (50)', 'box', False, False),
        ('N95 Respirator', 'piece', False, False),
        ('Face Shield', 'piece', False, False),
        ('Nitrile Gloves (100)', 'box', False, False),
        ('Latex Gloves (100)', 'box', False, False),
        ('Surgical Gown', 'piece', False, False),
        ('Shoe Cover (100 pairs)', 'pack', False, False),
        ('Hair Cap (100)', 'pack', False, False),
        ('Safety Goggles', 'piece', False, False),
    ],
    'Sterilization Equipment': [
        ('Autoclave 23L', 'piece', False, False),
        ('UV Sterilizer Cabinet', 'piece', False, False),
        ('Sterilization Pouches (200)', 'pack', False, False),
        ('Chemical Indicator Tape', 'roll', False, False),
        ('Disinfection Tray', 'piece', False, False),
    ],
    'Ophthalmic Equipment': [
        ('Slit Lamp', 'piece', False, False),
        ('Tonometer (Non-Contact)', 'piece', False, False),
        ('Snellen Chart', 'piece', False, False),
        ('Direct Ophthalmoscope', 'piece', False, False),
        ('Eye Patch', 'piece', False, False),
        ('Trial Lens Set', 'set', False, False),
    ],
    'Emergency & Resuscitation': [
        ('Automated External Defibrillator (AED)', 'piece', False, False),
        ('Ambu Bag (BVM)', 'piece', False, False),
        ('Oxygen Cylinder (10L)', 'piece', False, False),
        ('Oxygen Mask (10)', 'pack', False, False),
        ('Suction Machine (Electric)', 'piece', False, False),
        ('Laryngoscope Set', 'set', False, False),
        ('Endotracheal Tubes (10)', 'pack', False, False),
        ('Emergency Crash Cart', 'piece', False, False),
        ('First Aid Kit (Complete)', 'set', False, False),
    ],
}


MEDICINES_DATA = [
    # (generic_name, brand_name, dosage_form, strength, route, therapeutic_cat, prescription, narcotic, psychotropic, storage)
    # Analgesics & NSAIDs
    ('Paracetamol', 'Panadol', 'tablet', '500mg', 'oral', 'Analgesics & NSAIDs', False, False, False, 'room_temp'),
    ('Paracetamol', 'Calpol', 'syrup', '125mg/5ml', 'oral', 'Analgesics & NSAIDs', False, False, False, 'room_temp'),
    ('Ibuprofen', 'Brufen', 'tablet', '400mg', 'oral', 'Analgesics & NSAIDs', False, False, False, 'room_temp'),
    ('Diclofenac Sodium', 'Voltaren', 'tablet', '50mg', 'oral', 'Analgesics & NSAIDs', True, False, False, 'room_temp'),
    ('Diclofenac Sodium', 'Voltaren', 'injection', '75mg/3ml', 'injection_im', 'Analgesics & NSAIDs', True, False, False, 'room_temp'),
    ('Aspirin', 'Aspro', 'tablet', '100mg', 'oral', 'Analgesics & NSAIDs', False, False, False, 'room_temp'),
    ('Morphine Sulfate', 'MST', 'injection', '10mg/ml', 'injection_iv', 'Analgesics & NSAIDs', True, True, False, 'protect_light'),
    ('Tramadol HCl', 'Tramal', 'capsule', '50mg', 'oral', 'Analgesics & NSAIDs', True, False, False, 'room_temp'),
    ('Codeine Phosphate', 'Codeine', 'tablet', '30mg', 'oral', 'Analgesics & NSAIDs', True, True, False, 'room_temp'),
    ('Ketoprofen', 'Profenid', 'capsule', '100mg', 'oral', 'Analgesics & NSAIDs', True, False, False, 'room_temp'),

    # Antibiotics
    ('Amoxicillin', 'Amoxil', 'capsule', '250mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Amoxicillin', 'Amoxil', 'capsule', '500mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Amoxicillin Trihydrate', 'Amoxil', 'powder', '125mg/5ml', 'oral', 'Antibiotics', True, False, False, 'cool'),
    ('Amoxicillin + Clavulanate', 'Augmentin', 'tablet', '625mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Ampicillin Sodium', 'Pentrexyl', 'injection', '500mg', 'injection_im', 'Antibiotics', True, False, False, 'room_temp'),
    ('Benzylpenicillin', 'Crystapen', 'injection', '1MU', 'injection_im', 'Antibiotics', True, False, False, 'refrigerate'),
    ('Benzylpenicillin', 'Crystapen', 'injection', '5MU', 'injection_iv', 'Antibiotics', True, False, False, 'refrigerate'),
    ('Ciprofloxacin HCl', 'Cipro', 'tablet', '500mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Ciprofloxacin', 'Cipro', 'infusion', '200mg/100ml', 'injection_iv', 'Antibiotics', True, False, False, 'room_temp'),
    ('Doxycycline HCl', 'Vibramycin', 'capsule', '100mg', 'oral', 'Antibiotics', True, False, False, 'protect_light'),
    ('Erythromycin', 'Erythrocin', 'tablet', '250mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Erythromycin', 'Erythrocin', 'tablet', '500mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Metronidazole', 'Flagyl', 'tablet', '200mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Metronidazole', 'Flagyl', 'tablet', '400mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Metronidazole', 'Flagyl', 'infusion', '500mg/100ml', 'injection_iv', 'Antibiotics', True, False, False, 'room_temp'),
    ('Cotrimoxazole', 'Septrin', 'tablet', '480mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Cotrimoxazole', 'Septrin', 'tablet', '960mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Cloxacillin Sodium', 'Orbenin', 'capsule', '500mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Ceftriaxone Sodium', 'Rocephin', 'injection', '1g', 'injection_iv', 'Antibiotics', True, False, False, 'room_temp'),
    ('Cefazolin Sodium', 'Ancef', 'injection', '1g', 'injection_iv', 'Antibiotics', True, False, False, 'room_temp'),
    ('Gentamicin Sulfate', 'Garamycin', 'injection', '80mg/2ml', 'injection_im', 'Antibiotics', True, False, False, 'room_temp'),
    ('Chloramphenicol', 'Chloromycetin', 'capsule', '250mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Azithromycin', 'Zithromax', 'tablet', '250mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Azithromycin', 'Zithromax', 'tablet', '500mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Clindamycin HCl', 'Dalacin', 'capsule', '150mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),
    ('Clindamycin HCl', 'Dalacin', 'capsule', '300mg', 'oral', 'Antibiotics', True, False, False, 'room_temp'),

    # Antimalarials
    ('Artemether + Lumefantrine', 'Coartem', 'tablet', '20mg+120mg', 'oral', 'Antimalarials', True, False, False, 'room_temp'),
    ('Artesunate', 'Arsumax', 'injection', '60mg', 'injection_iv', 'Antimalarials', True, False, False, 'room_temp'),
    ('Chloroquine Phosphate', 'Resochin', 'tablet', '150mg base', 'oral', 'Antimalarials', True, False, False, 'room_temp'),
    ('Quinine Sulfate', 'Quinimax', 'tablet', '300mg', 'oral', 'Antimalarials', True, False, False, 'room_temp'),
    ('Quinine Dihydrochloride', 'Quinimax', 'injection', '600mg/2ml', 'injection_iv', 'Antimalarials', True, False, False, 'protect_light'),
    ('Primaquine Phosphate', 'Primaquine', 'tablet', '15mg', 'oral', 'Antimalarials', True, False, False, 'room_temp'),

    # Antituberculosis
    ('Isoniazid (H)', 'INH', 'tablet', '100mg', 'oral', 'Antituberculosis', True, False, False, 'protect_light'),
    ('Isoniazid (H)', 'INH', 'tablet', '300mg', 'oral', 'Antituberculosis', True, False, False, 'protect_light'),
    ('Rifampicin (R)', 'Rifadin', 'capsule', '150mg', 'oral', 'Antituberculosis', True, False, False, 'protect_light'),
    ('Rifampicin (R)', 'Rifadin', 'capsule', '300mg', 'oral', 'Antituberculosis', True, False, False, 'protect_light'),
    ('Pyrazinamide (Z)', 'Pyrazinamide', 'tablet', '400mg', 'oral', 'Antituberculosis', True, False, False, 'room_temp'),
    ('Pyrazinamide (Z)', 'Pyrazinamide', 'tablet', '500mg', 'oral', 'Antituberculosis', True, False, False, 'room_temp'),
    ('Ethambutol HCl (E)', 'Myambutol', 'tablet', '400mg', 'oral', 'Antituberculosis', True, False, False, 'room_temp'),
    ('Streptomycin Sulfate', 'Streptomycin', 'injection', '1g', 'injection_im', 'Antituberculosis', True, False, False, 'refrigerate'),
    ('RHZE (Fixed Dose Combo)', 'Rifater', 'tablet', '150+75+400+275mg', 'oral', 'Antituberculosis', True, False, False, 'protect_light'),
    ('RH (Fixed Dose Combo)', 'Rifinah', 'tablet', '150+75mg', 'oral', 'Antituberculosis', True, False, False, 'protect_light'),

    # Antiretrovirals
    ('TDF+3TC+EFV (TLE)', 'Atripla', 'tablet', '300+300+600mg', 'oral', 'Antiretrovirals', True, False, False, 'room_temp'),
    ('TDF+3TC+DTG (TLD)', 'Triumeq', 'tablet', '300+300+50mg', 'oral', 'Antiretrovirals', True, False, False, 'room_temp'),
    ('AZT+3TC+NVP', 'Trivenz', 'tablet', '300+150+200mg', 'oral', 'Antiretrovirals', True, False, False, 'room_temp'),
    ('Lopinavir + Ritonavir', 'Kaletra', 'tablet', '200+50mg', 'oral', 'Antiretrovirals', True, False, False, 'refrigerate'),
    ('Abacavir Sulfate', 'Ziagen', 'tablet', '300mg', 'oral', 'Antiretrovirals', True, False, False, 'room_temp'),
    ('Lamivudine (3TC)', 'Epivir', 'tablet', '150mg', 'oral', 'Antiretrovirals', True, False, False, 'room_temp'),
    ('Nevirapine', 'Viramune', 'tablet', '200mg', 'oral', 'Antiretrovirals', True, False, False, 'room_temp'),
    ('Efavirenz', 'Sustiva', 'capsule', '200mg', 'oral', 'Antiretrovirals', True, False, False, 'room_temp'),
    ('Efavirenz', 'Sustiva', 'tablet', '600mg', 'oral', 'Antiretrovirals', True, False, False, 'room_temp'),

    # Antifungals
    ('Fluconazole', 'Diflucan', 'capsule', '150mg', 'oral', 'Antifungals', True, False, False, 'room_temp'),
    ('Fluconazole', 'Diflucan', 'capsule', '200mg', 'oral', 'Antifungals', True, False, False, 'room_temp'),
    ('Griseofulvin', 'Fulvicin', 'tablet', '125mg', 'oral', 'Antifungals', True, False, False, 'room_temp'),
    ('Clotrimazole', 'Canesten', 'cream', '1%', 'topical', 'Antifungals', False, False, False, 'room_temp'),
    ('Clotrimazole', 'Canesten', 'pessary', '100mg', 'vaginal', 'Antifungals', False, False, False, 'room_temp'),
    ('Nystatin', 'Mycostatin', 'drops', '100,000IU/ml', 'oral', 'Antifungals', False, False, False, 'refrigerate'),
    ('Amphotericin B', 'Fungizone', 'injection', '50mg', 'injection_iv', 'Antifungals', True, False, False, 'refrigerate'),
    ('Ketoconazole', 'Nizoral', 'tablet', '200mg', 'oral', 'Antifungals', True, False, False, 'room_temp'),

    # Antiparasitic
    ('Albendazole', 'Zentel', 'tablet', '400mg', 'oral', 'Antiparasitic', False, False, False, 'room_temp'),
    ('Mebendazole', 'Vermox', 'tablet', '100mg', 'oral', 'Antiparasitic', False, False, False, 'room_temp'),
    ('Mebendazole', 'Vermox', 'tablet', '500mg', 'oral', 'Antiparasitic', False, False, False, 'room_temp'),
    ('Praziquantel', 'Biltricide', 'tablet', '600mg', 'oral', 'Antiparasitic', True, False, False, 'room_temp'),
    ('Ivermectin', 'Mectizan', 'tablet', '3mg', 'oral', 'Antiparasitic', True, False, False, 'room_temp'),

    # Cardiovascular
    ('Amlodipine Besylate', 'Norvasc', 'tablet', '5mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Amlodipine Besylate', 'Norvasc', 'tablet', '10mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Atenolol', 'Tenormin', 'tablet', '50mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Atenolol', 'Tenormin', 'tablet', '100mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Captopril', 'Capoten', 'tablet', '25mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Captopril', 'Capoten', 'tablet', '50mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Enalapril Maleate', 'Vasotec', 'tablet', '5mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Enalapril Maleate', 'Vasotec', 'tablet', '10mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Furosemide', 'Lasix', 'tablet', '40mg', 'oral', 'Cardiovascular', True, False, False, 'protect_light'),
    ('Furosemide', 'Lasix', 'injection', '20mg/2ml', 'injection_iv', 'Cardiovascular', True, False, False, 'protect_light'),
    ('Hydrochlorothiazide', 'HydroDIURIL', 'tablet', '25mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Methyldopa', 'Aldomet', 'tablet', '250mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Methyldopa', 'Aldomet', 'tablet', '500mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Nifedipine', 'Adalat', 'tablet', '10mg', 'oral', 'Cardiovascular', True, False, False, 'protect_light'),
    ('Nifedipine', 'Adalat', 'tablet', '20mg', 'oral', 'Cardiovascular', True, False, False, 'protect_light'),
    ('Digoxin', 'Lanoxin', 'tablet', '0.25mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Digoxin', 'Lanoxin', 'injection', '0.25mg/ml', 'injection_iv', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Propranolol HCl', 'Inderal', 'tablet', '40mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Propranolol HCl', 'Inderal', 'tablet', '80mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Spironolactone', 'Aldactone', 'tablet', '25mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Verapamil HCl', 'Isoptin', 'tablet', '80mg', 'oral', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Isosorbide Dinitrate', 'Isordil', 'tablet', '5mg', 'sublingual', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Glyceryl Trinitrate', 'Nitrolingual', 'spray', '400mcg/dose', 'sublingual', 'Cardiovascular', True, False, False, 'room_temp'),
    ('Warfarin Sodium', 'Coumadin', 'tablet', '1mg', 'oral', 'Cardiovascular', True, False, False, 'protect_light'),
    ('Warfarin Sodium', 'Coumadin', 'tablet', '5mg', 'oral', 'Cardiovascular', True, False, False, 'protect_light'),
    ('Heparin Sodium', 'Heparin', 'injection', '5000IU/ml', 'injection_iv', 'Cardiovascular', True, False, False, 'room_temp'),

    # Diabetes
    ('Glibenclamide', 'Daonil', 'tablet', '5mg', 'oral', 'Diabetes Medicines', True, False, False, 'room_temp'),
    ('Metformin HCl', 'Glucophage', 'tablet', '500mg', 'oral', 'Diabetes Medicines', True, False, False, 'room_temp'),
    ('Metformin HCl', 'Glucophage', 'tablet', '850mg', 'oral', 'Diabetes Medicines', True, False, False, 'room_temp'),
    ('Metformin HCl', 'Glucophage', 'tablet', '1000mg', 'oral', 'Diabetes Medicines', True, False, False, 'room_temp'),
    ('Insulin Regular', 'Actrapid', 'injection', '100IU/ml (10ml)', 'injection_sc', 'Diabetes Medicines', True, False, False, 'refrigerate'),
    ('Insulin NPH', 'Protaphane', 'injection', '100IU/ml (10ml)', 'injection_sc', 'Diabetes Medicines', True, False, False, 'refrigerate'),
    ('Insulin Glargine', 'Lantus', 'injection', '100IU/ml (10ml)', 'injection_sc', 'Diabetes Medicines', True, False, False, 'refrigerate'),
    ('Insulin Mixtard 30/70', 'Mixtard', 'injection', '100IU/ml (10ml)', 'injection_sc', 'Diabetes Medicines', True, False, False, 'refrigerate'),
    ('Glimepiride', 'Amaryl', 'tablet', '1mg', 'oral', 'Diabetes Medicines', True, False, False, 'room_temp'),
    ('Glimepiride', 'Amaryl', 'tablet', '2mg', 'oral', 'Diabetes Medicines', True, False, False, 'room_temp'),
    ('Glimepiride', 'Amaryl', 'tablet', '4mg', 'oral', 'Diabetes Medicines', True, False, False, 'room_temp'),

    # Gastrointestinal
    ('Omeprazole', 'Losec', 'capsule', '20mg', 'oral', 'Gastrointestinal', False, False, False, 'room_temp'),
    ('Omeprazole', 'Losec', 'capsule', '40mg', 'oral', 'Gastrointestinal', False, False, False, 'room_temp'),
    ('Ranitidine HCl', 'Zantac', 'tablet', '150mg', 'oral', 'Gastrointestinal', False, False, False, 'room_temp'),
    ('Ranitidine HCl', 'Zantac', 'tablet', '300mg', 'oral', 'Gastrointestinal', False, False, False, 'room_temp'),
    ('Metoclopramide HCl', 'Maxolon', 'tablet', '10mg', 'oral', 'Gastrointestinal', True, False, False, 'room_temp'),
    ('Metoclopramide HCl', 'Maxolon', 'injection', '10mg/2ml', 'injection_im', 'Gastrointestinal', True, False, False, 'room_temp'),
    ('Ondansetron HCl', 'Zofran', 'tablet', '4mg', 'oral', 'Gastrointestinal', True, False, False, 'room_temp'),
    ('Ondansetron HCl', 'Zofran', 'tablet', '8mg', 'oral', 'Gastrointestinal', True, False, False, 'room_temp'),
    ('Ondansetron', 'Zofran', 'injection', '4mg/2ml', 'injection_iv', 'Gastrointestinal', True, False, False, 'room_temp'),
    ('Bisacodyl', 'Dulcolax', 'tablet', '5mg', 'oral', 'Gastrointestinal', False, False, False, 'room_temp'),
    ('Senna', 'Senokot', 'tablet', '7.5mg', 'oral', 'Gastrointestinal', False, False, False, 'room_temp'),
    ('Lactulose', 'Duphalac', 'syrup', '3.3g/5ml', 'oral', 'Gastrointestinal', False, False, False, 'room_temp'),
    ('Loperamide HCl', 'Imodium', 'capsule', '2mg', 'oral', 'Gastrointestinal', False, False, False, 'room_temp'),
    ('Oral Rehydration Salts', 'ORS', 'sachet', '20.5g', 'oral', 'Gastrointestinal', False, False, False, 'room_temp'),
    ('Zinc Sulfate', 'Zn Sulfate', 'tablet', '20mg', 'oral', 'Gastrointestinal', False, False, False, 'room_temp'),
    ('Antacid (Al+Mg)', 'Maalox', 'suspension', '200+200mg/5ml', 'oral', 'Gastrointestinal', False, False, False, 'room_temp'),

    # Respiratory
    ('Salbutamol', 'Ventolin', 'tablet', '2mg', 'oral', 'Respiratory', False, False, False, 'room_temp'),
    ('Salbutamol', 'Ventolin', 'tablet', '4mg', 'oral', 'Respiratory', False, False, False, 'room_temp'),
    ('Salbutamol', 'Ventolin', 'inhaler', '100mcg/dose', 'inhalation', 'Respiratory', False, False, False, 'room_temp'),
    ('Salbutamol', 'Ventolin', 'solution', '2.5mg/2.5ml', 'inhalation', 'Respiratory', False, False, False, 'room_temp'),
    ('Aminophylline', 'Phyllocontin', 'tablet', '100mg', 'oral', 'Respiratory', True, False, False, 'room_temp'),
    ('Aminophylline', 'Phyllocontin', 'injection', '250mg/10ml', 'injection_iv', 'Respiratory', True, False, False, 'room_temp'),
    ('Prednisolone', 'Deltacortril', 'tablet', '5mg', 'oral', 'Respiratory', True, False, False, 'room_temp'),
    ('Prednisolone', 'Deltacortril', 'tablet', '25mg', 'oral', 'Respiratory', True, False, False, 'room_temp'),
    ('Dexamethasone', 'Decadron', 'injection', '4mg/ml', 'injection_iv', 'Respiratory', True, False, False, 'room_temp'),
    ('Hydrocortisone Sodium Succinate', 'Solu-Cortef', 'injection', '100mg', 'injection_iv', 'Respiratory', True, False, False, 'room_temp'),
    ('Budesonide', 'Pulmicort', 'inhaler', '200mcg/dose', 'inhalation', 'Respiratory', True, False, False, 'room_temp'),
    ('Ipratropium Bromide', 'Atrovent', 'inhaler', '20mcg/dose', 'inhalation', 'Respiratory', True, False, False, 'room_temp'),
    ('Beclomethasone Dipropionate', 'Becloforte', 'inhaler', '250mcg/dose', 'inhalation', 'Respiratory', True, False, False, 'room_temp'),
    ('N-Acetylcysteine', 'Fluimucil', 'effervescent', '600mg', 'oral', 'Respiratory', False, False, False, 'room_temp'),

    # Psychiatric & Neurological
    ('Haloperidol', 'Haldol', 'tablet', '5mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Haloperidol', 'Haldol', 'injection', '5mg/ml', 'injection_im', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Chlorpromazine HCl', 'Largactil', 'tablet', '100mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'protect_light'),
    ('Chlorpromazine HCl', 'Largactil', 'tablet', '200mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'protect_light'),
    ('Diazepam', 'Valium', 'tablet', '5mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Diazepam', 'Valium', 'tablet', '10mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Diazepam', 'Valium', 'injection', '10mg/2ml', 'injection_iv', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Phenobarbitone', 'Luminal', 'tablet', '30mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Phenobarbitone', 'Luminal', 'tablet', '60mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Phenobarbitone', 'Luminal', 'tablet', '100mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Phenytoin Sodium', 'Epanutin', 'capsule', '100mg', 'oral', 'Psychiatric & Neurological', True, False, False, 'room_temp'),
    ('Carbamazepine', 'Tegretol', 'tablet', '200mg', 'oral', 'Psychiatric & Neurological', True, False, False, 'room_temp'),
    ('Carbamazepine', 'Tegretol', 'tablet', '400mg', 'oral', 'Psychiatric & Neurological', True, False, False, 'room_temp'),
    ('Sodium Valproate', 'Epilim', 'tablet', '200mg', 'oral', 'Psychiatric & Neurological', True, False, False, 'room_temp'),
    ('Sodium Valproate', 'Epilim', 'tablet', '500mg', 'oral', 'Psychiatric & Neurological', True, False, False, 'room_temp'),
    ('Amitriptyline HCl', 'Tryptizol', 'tablet', '25mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Amitriptyline HCl', 'Tryptizol', 'tablet', '50mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Fluoxetine HCl', 'Prozac', 'capsule', '20mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Risperidone', 'Risperdal', 'tablet', '1mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Risperidone', 'Risperdal', 'tablet', '2mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Lithium Carbonate', 'Camcolit', 'tablet', '300mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Lorazepam', 'Ativan', 'injection', '4mg/ml', 'injection_iv', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Clonazepam', 'Rivotril', 'tablet', '0.5mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Clonazepam', 'Rivotril', 'tablet', '2mg', 'oral', 'Psychiatric & Neurological', True, False, True, 'room_temp'),
    ('Levodopa + Carbidopa', 'Sinemet', 'tablet', '100+25mg', 'oral', 'Psychiatric & Neurological', True, False, False, 'room_temp'),

    # Vitamins & Minerals
    ('Folic Acid', 'Folvite', 'tablet', '5mg', 'oral', 'Vitamins & Minerals', False, False, False, 'room_temp'),
    ('Ferrous Sulfate', 'Feosol', 'tablet', '200mg (65mg Fe)', 'oral', 'Vitamins & Minerals', False, False, False, 'room_temp'),
    ('Ferrous Sulfate + Folic Acid', 'Ferrograd Folic', 'tablet', '200mg+0.4mg', 'oral', 'Vitamins & Minerals', False, False, False, 'room_temp'),
    ('Vitamin A', 'Vitamin A caps', 'capsule', '100,000 IU', 'oral', 'Vitamins & Minerals', False, False, False, 'cool'),
    ('Vitamin A', 'Vitamin A caps', 'capsule', '200,000 IU', 'oral', 'Vitamins & Minerals', False, False, False, 'cool'),
    ('Vitamin B Complex', 'Polyvitamin', 'tablet', 'Standard', 'oral', 'Vitamins & Minerals', False, False, False, 'room_temp'),
    ('Vitamin C (Ascorbic Acid)', 'Redoxon', 'tablet', '100mg', 'oral', 'Vitamins & Minerals', False, False, False, 'room_temp'),
    ('Vitamin C (Ascorbic Acid)', 'Redoxon', 'tablet', '500mg', 'oral', 'Vitamins & Minerals', False, False, False, 'room_temp'),
    ('Vitamin D3 (Cholecalciferol)', 'Vigantol', 'capsule', '1000IU', 'oral', 'Vitamins & Minerals', False, False, False, 'cool'),
    ('Vitamin D3 (Cholecalciferol)', 'Vigantol', 'capsule', '5000IU', 'oral', 'Vitamins & Minerals', False, False, False, 'cool'),
    ('Calcium Carbonate', 'Calcimax', 'tablet', '500mg', 'oral', 'Vitamins & Minerals', False, False, False, 'room_temp'),
    ('Calcium Carbonate', 'Calcimax', 'tablet', '1000mg', 'oral', 'Vitamins & Minerals', False, False, False, 'room_temp'),
    ('Zinc Sulfate', 'Zincomed', 'tablet', '20mg', 'oral', 'Vitamins & Minerals', False, False, False, 'room_temp'),
    ('Multivitamin + Minerals', 'Centrum', 'tablet', 'Standard', 'oral', 'Vitamins & Minerals', False, False, False, 'room_temp'),
    ('Thiamine (B1)', 'Benerva', 'tablet', '100mg', 'oral', 'Vitamins & Minerals', False, False, False, 'room_temp'),

    # Ophthalmology
    ('Tetracycline', 'Tetracycline Eye Ointment', 'ointment', '1%', 'ophthalmic', 'Ophthalmology', True, False, False, 'cool'),
    ('Chloramphenicol', 'Chloromycetin', 'drops', '0.5%', 'ophthalmic', 'Ophthalmology', True, False, False, 'refrigerate'),
    ('Ciprofloxacin', 'Ciloxan', 'drops', '0.3%', 'ophthalmic', 'Ophthalmology', True, False, False, 'room_temp'),
    ('Gentamicin Sulfate', 'Garamycin Eye Drops', 'drops', '0.3%', 'ophthalmic', 'Ophthalmology', True, False, False, 'room_temp'),
    ('Pilocarpine HCl', 'Pilocarpine', 'drops', '2%', 'ophthalmic', 'Ophthalmology', True, False, False, 'refrigerate'),
    ('Timolol Maleate', 'Timoptol', 'drops', '0.5%', 'ophthalmic', 'Ophthalmology', True, False, False, 'room_temp'),
    ('Prednisolone Acetate', 'Pred Forte', 'drops', '1%', 'ophthalmic', 'Ophthalmology', True, False, False, 'room_temp'),
    ('Tropicamide', 'Mydriacyl', 'drops', '1%', 'ophthalmic', 'Ophthalmology', True, False, False, 'room_temp'),

    # Dermatology
    ('Betamethasone Valerate', 'Betnovate', 'cream', '0.1%', 'topical', 'Dermatology', True, False, False, 'room_temp'),
    ('Hydrocortisone', 'Hydrocortisone Cream', 'cream', '1%', 'topical', 'Dermatology', False, False, False, 'room_temp'),
    ('Calamine', 'Calamine Lotion', 'lotion', '15%', 'topical', 'Dermatology', False, False, False, 'room_temp'),
    ('Whitfield Ointment', 'Whitfield', 'ointment', 'Compound', 'topical', 'Dermatology', False, False, False, 'room_temp'),
    ('Permethrin', 'Lyclear', 'cream', '5%', 'topical', 'Dermatology', True, False, False, 'room_temp'),
    ('Benzoyl Peroxide', 'Benzac', 'gel', '5%', 'topical', 'Dermatology', False, False, False, 'room_temp'),
    ('Salicylic Acid', 'Compound W', 'solution', '2-6%', 'topical', 'Dermatology', False, False, False, 'room_temp'),

    # Obstetrics & Gynecology
    ('Oxytocin', 'Syntocinon', 'injection', '10IU/ml', 'injection_im', 'Obstetrics & Gynecology', True, False, False, 'refrigerate'),
    ('Ergometrine Maleate', 'Ergometrine', 'injection', '0.5mg/ml', 'injection_im', 'Obstetrics & Gynecology', True, False, False, 'refrigerate'),
    ('Misoprostol', 'Cytotec', 'tablet', '200mcg', 'oral', 'Obstetrics & Gynecology', True, False, False, 'cool'),
    ('Magnesium Sulfate', 'MgSO4', 'injection', '50% (5g/10ml)', 'injection_iv', 'Obstetrics & Gynecology', True, False, False, 'room_temp'),
    ('Hydralazine HCl', 'Apresoline', 'injection', '20mg/ml', 'injection_iv', 'Obstetrics & Gynecology', True, False, False, 'protect_light'),
    ('Combined Oral Contraceptive', 'Microgynon', 'tablet', '30mcg EE+150mcg LNG', 'oral', 'Obstetrics & Gynecology', True, False, False, 'room_temp'),
    ('Levonorgestrel', 'Postinor-2', 'tablet', '750mcg', 'oral', 'Obstetrics & Gynecology', True, False, False, 'room_temp'),
    ('Depot Medroxyprogesterone', 'Depo-Provera', 'injection', '150mg/ml', 'injection_im', 'Obstetrics & Gynecology', True, False, False, 'refrigerate'),
    ('Norethisterone Enanthate', 'Noristerat', 'injection', '200mg/ml', 'injection_im', 'Obstetrics & Gynecology', True, False, False, 'room_temp'),
    ('Clomiphene Citrate', 'Clomid', 'tablet', '50mg', 'oral', 'Obstetrics & Gynecology', True, False, False, 'room_temp'),
    ('Progesterone', 'Utrogestan', 'capsule', '200mg', 'oral', 'Obstetrics & Gynecology', True, False, False, 'room_temp'),

    # Anesthesia & Emergency
    ('Ketamine HCl', 'Ketalar', 'injection', '500mg/10ml', 'injection_iv', 'Anesthesia & Emergency', True, True, False, 'protect_light'),
    ('Thiopentone Sodium', 'Pentothal', 'injection', '500mg', 'injection_iv', 'Anesthesia & Emergency', True, False, False, 'room_temp'),
    ('Atropine Sulfate', 'Atropine', 'injection', '0.5mg/ml', 'injection_im', 'Anesthesia & Emergency', True, False, False, 'room_temp'),
    ('Adrenaline (Epinephrine)', 'EpiPen', 'injection', '1mg/ml', 'injection_iv', 'Anesthesia & Emergency', True, False, False, 'protect_light'),
    ('Lidocaine HCl', 'Lignocaine', 'injection', '1%', 'injection_im', 'Anesthesia & Emergency', True, False, False, 'room_temp'),
    ('Lidocaine HCl', 'Lignocaine', 'injection', '2%', 'injection_im', 'Anesthesia & Emergency', True, False, False, 'room_temp'),
    ('Bupivacaine HCl', 'Marcaine', 'injection', '0.5%', 'injection_im', 'Anesthesia & Emergency', True, False, False, 'room_temp'),
    ('Suxamethonium Chloride', 'Anectine', 'injection', '200mg/10ml', 'injection_iv', 'Anesthesia & Emergency', True, False, False, 'refrigerate'),
    ('Rocuronium Bromide', 'Esmeron', 'injection', '50mg/5ml', 'injection_iv', 'Anesthesia & Emergency', True, False, False, 'refrigerate'),
    ('Neostigmine Methylsulfate', 'Prostigmin', 'injection', '2.5mg/ml', 'injection_iv', 'Anesthesia & Emergency', True, False, False, 'room_temp'),
    ('Naloxone HCl', 'Narcan', 'injection', '400mcg/ml', 'injection_iv', 'Anesthesia & Emergency', True, False, False, 'room_temp'),
    ('Flumazenil', 'Anexate', 'injection', '200mcg/2ml', 'injection_iv', 'Anesthesia & Emergency', True, False, False, 'room_temp'),
    ('Dopamine HCl', 'Intropin', 'injection', '200mg/5ml', 'injection_iv', 'Anesthesia & Emergency', True, False, False, 'protect_light'),
    ('Dobutamine HCl', 'Dobutrex', 'injection', '250mg/20ml', 'injection_iv', 'Anesthesia & Emergency', True, False, False, 'room_temp'),
    ('Adenosine', 'Adenocard', 'injection', '6mg/2ml', 'injection_iv', 'Anesthesia & Emergency', True, False, False, 'room_temp'),
    ('Noradrenaline', 'Levophed', 'injection', '4mg/4ml', 'injection_iv', 'Anesthesia & Emergency', True, False, False, 'protect_light'),

    # IV Fluids
    ('Normal Saline 0.9%', 'Normal Saline', 'infusion', '500ml', 'injection_iv', 'IV Fluids & Solutions', False, False, False, 'room_temp'),
    ('Normal Saline 0.9%', 'Normal Saline', 'infusion', '1000ml', 'injection_iv', 'IV Fluids & Solutions', False, False, False, 'room_temp'),
    ('Dextrose 5%', 'Dextrose 5%', 'infusion', '500ml', 'injection_iv', 'IV Fluids & Solutions', False, False, False, 'room_temp'),
    ('Dextrose 5%', 'Dextrose 5%', 'infusion', '1000ml', 'injection_iv', 'IV Fluids & Solutions', False, False, False, 'room_temp'),
    ('Dextrose-Saline (0.9%+5%)', 'Dextrose-Saline', 'infusion', '500ml', 'injection_iv', 'IV Fluids & Solutions', False, False, False, 'room_temp'),
    ("Ringer's Lactate", "Ringer's Lactate", 'infusion', '500ml', 'injection_iv', 'IV Fluids & Solutions', False, False, False, 'room_temp'),
    ("Ringer's Lactate", "Ringer's Lactate", 'infusion', '1000ml', 'injection_iv', 'IV Fluids & Solutions', False, False, False, 'room_temp'),
    ('Dextrose 50%', 'Dextrose 50%', 'injection', '50ml', 'injection_iv', 'IV Fluids & Solutions', True, False, False, 'room_temp'),
    ('Sodium Bicarbonate 8.4%', 'NaHCO3', 'infusion', '100ml', 'injection_iv', 'IV Fluids & Solutions', True, False, False, 'room_temp'),
    ('Mannitol 20%', 'Osmitrol', 'infusion', '250ml', 'injection_iv', 'IV Fluids & Solutions', True, False, False, 'room_temp'),

    # Vaccines
    ('BCG Vaccine', 'BCG', 'injection', '0.1ml/dose', 'injection_sc', 'Vaccines', False, False, False, 'freeze'),
    ('OPV (Oral Polio Vaccine)', 'OPV', 'drops', '2 drops/dose', 'oral', 'Vaccines', False, False, False, 'freeze'),
    ('DPT-HepB-Hib (Pentavalent)', 'Pentavalent', 'injection', '0.5ml/dose', 'injection_im', 'Vaccines', False, False, False, 'refrigerate'),
    ('PCV-10 (Pneumococcal)', 'Synflorix', 'injection', '0.5ml/dose', 'injection_im', 'Vaccines', False, False, False, 'refrigerate'),
    ('Rotavirus Vaccine (Rotarix)', 'Rotarix', 'drops', '1.5ml/dose', 'oral', 'Vaccines', False, False, False, 'refrigerate'),
    ('IPV (Inactivated Polio)', 'IPV', 'injection', '0.5ml/dose', 'injection_sc', 'Vaccines', False, False, False, 'refrigerate'),
    ('Measles-Rubella Vaccine', 'MR Vaccine', 'injection', '0.5ml/dose', 'injection_sc', 'Vaccines', False, False, False, 'freeze'),
    ('Yellow Fever Vaccine', 'Stamaril', 'injection', '0.5ml/dose', 'injection_sc', 'Vaccines', False, False, False, 'freeze'),
    ('Hepatitis B Vaccine', 'Engerix-B', 'injection', '1ml/dose', 'injection_im', 'Vaccines', False, False, False, 'refrigerate'),
    ('Tetanus Toxoid', 'TT Vaccine', 'injection', '0.5ml/dose', 'injection_im', 'Vaccines', False, False, False, 'refrigerate'),
    ('Rabies Vaccine', 'Rabipur', 'injection', '1ml/dose', 'injection_im', 'Vaccines', False, False, False, 'refrigerate'),
    ('Typhoid Vaccine', 'Typhim Vi', 'injection', '0.5ml/dose', 'injection_im', 'Vaccines', False, False, False, 'refrigerate'),
    ('Meningococcal Vaccine', 'MenAfriVac', 'injection', '0.5ml/dose', 'injection_im', 'Vaccines', False, False, False, 'refrigerate'),

    # Disinfectants & Antiseptics
    ('Chlorhexidine Gluconate', 'Hibiscrub', 'solution', '4% (500ml)', 'topical', 'Disinfectants & Antiseptics', False, False, False, 'room_temp'),
    ('Chlorhexidine', 'Chlorhex', 'solution', '7.1% (umbilical cord)', 'topical', 'Disinfectants & Antiseptics', False, False, False, 'room_temp'),
    ('Ethanol 70%', 'Methylated Spirit', 'solution', '70% (1L)', 'topical', 'Disinfectants & Antiseptics', False, False, False, 'room_temp'),
    ('Isopropyl Alcohol 70%', 'IPA 70%', 'solution', '70% (1L)', 'topical', 'Disinfectants & Antiseptics', False, False, False, 'room_temp'),
    ('Povidone-Iodine', 'Betadine', 'solution', '10% (500ml)', 'topical', 'Disinfectants & Antiseptics', False, False, False, 'protect_light'),
    ('Hydrogen Peroxide', 'H2O2', 'solution', '3% (500ml)', 'topical', 'Disinfectants & Antiseptics', False, False, False, 'protect_light'),
    ('Sodium Hypochlorite', 'Bleach', 'solution', '0.1% (1L)', 'topical', 'Disinfectants & Antiseptics', False, False, False, 'room_temp'),
    ('Hand Sanitizer (Alcohol-based)', 'Purell', 'gel', '70% Ethanol (500ml)', 'topical', 'Disinfectants & Antiseptics', False, False, False, 'room_temp'),
    ('Iodine Tincture', 'Iodine', 'solution', '2% (100ml)', 'topical', 'Disinfectants & Antiseptics', False, False, False, 'protect_light'),
]


class Command(BaseCommand):
    help = 'Load initial data: categories, products, medicines, warehouse, admin user'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data load...'))
        self._create_admin_user()
        self._create_warehouse()
        self._create_categories()
        self._create_equipment_products()
        self._create_medicines()
        self.stdout.write(self.style.SUCCESS('All data loaded successfully!'))

    def _create_admin_user(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@mediethiopia.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                role='admin',
                region='addis_ababa',
            )
            self.stdout.write(self.style.SUCCESS('Admin user created (admin/admin123)'))
        else:
            self.stdout.write('Admin user already exists')

    def _create_warehouse(self):
        from warehouse.models import Warehouse
        if not Warehouse.objects.exists():
            admin = User.objects.filter(username='admin').first()
            Warehouse.objects.create(
                name='Main Warehouse - Addis Ababa',
                code='WH-AAB-001',
                address='Bole Sub-City, Woreda 3',
                city='Addis Ababa',
                region='Addis Ababa',
                manager=admin,
                phone='+251-11-123-4567',
                has_cold_storage=True,
                cold_storage_capacity=50.0,
            )
            Warehouse.objects.create(
                name='Hawassa Distribution Center',
                code='WH-HWS-001',
                address='Sidama Region, Hawassa City',
                city='Hawassa',
                region='Sidama',
                phone='+251-46-123-4567',
                has_cold_storage=False,
            )
            self.stdout.write(self.style.SUCCESS('Sample warehouses created'))
        else:
            self.stdout.write('Warehouses already exist')

    def _create_categories(self):
        from products.models import Category
        created = 0
        for name, description in EQUIPMENT_CATEGORIES + MEDICINE_CATEGORIES:
            obj, c = Category.objects.get_or_create(
                name=name,
                defaults={'description': description, 'slug': self._unique_slug(name, Category)}
            )
            if c:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'{created} categories created'))

    def _unique_slug(self, name, model):
        base = slugify(name)
        slug = base
        n = 1
        while model.objects.filter(slug=slug).exists():
            slug = f'{base}-{n}'
            n += 1
        return slug

    def _create_equipment_products(self):
        from products.models import Category, Product, ProductVariant
        created = 0
        for category_name, products in EQUIPMENT_PRODUCTS.items():
            try:
                cat = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Category not found: {category_name}'))
                continue
            for (name, unit, controlled, cold) in products:
                product, c = Product.objects.get_or_create(
                    name=name,
                    category=cat,
                    defaults={
                        'slug': self._unique_slug(name, Product),
                        'unit_of_measure': unit,
                        'is_controlled_substance': controlled,
                        'requires_cold_chain': cold,
                        'reorder_level': 5,
                        'is_active': True,
                    }
                )
                if c:
                    # Create a default variant
                    ProductVariant.objects.get_or_create(
                        product=product,
                        defaults={
                            'cost_price': 0,
                            'selling_price': 0,
                            'tax_category': 'taxable',
                        }
                    )
                    created += 1
        self.stdout.write(self.style.SUCCESS(f'{created} equipment products created'))

    def _create_medicines(self):
        from products.models import Category, Product, ProductVariant, Medicine
        medicine_cat, _ = Category.objects.get_or_create(
            name='Medicines',
            defaults={'description': 'All pharmaceutical medicines', 'slug': 'medicines'}
        )
        created = 0
        for med_data in MEDICINES_DATA:
            (generic_name, brand_name, dosage_form, strength, route,
             therapeutic_cat, prescription, narcotic, psychotropic, storage) = med_data

            # Get or create the therapeutic category
            try:
                cat = Category.objects.get(name=therapeutic_cat)
            except Category.DoesNotExist:
                cat = medicine_cat

            product_name = f"{generic_name} {strength}"
            product, p_created = Product.objects.get_or_create(
                name=product_name,
                category=cat,
                defaults={
                    'slug': self._unique_slug(product_name, Product),
                    'brand': brand_name,
                    'unit_of_measure': self._get_unit(dosage_form),
                    'is_controlled_substance': narcotic,
                    'reorder_level': 20,
                    'is_active': True,
                }
            )

            if p_created:
                # Create default variant
                ProductVariant.objects.get_or_create(
                    product=product,
                    defaults={
                        'strength': strength,
                        'cost_price': 0,
                        'selling_price': 0,
                        'tax_category': 'vat_exempt',
                    }
                )
                # Create medicine info
                Medicine.objects.get_or_create(
                    product=product,
                    defaults={
                        'generic_name': generic_name,
                        'brand_name': brand_name,
                        'dosage_form': dosage_form,
                        'strength': strength,
                        'route_of_administration': route,
                        'therapeutic_category': therapeutic_cat,
                        'prescription_required': prescription,
                        'is_narcotic': narcotic,
                        'is_psychotropic': psychotropic,
                        'storage_condition': storage,
                        'shelf_life_months': 24,
                    }
                )
                created += 1
        self.stdout.write(self.style.SUCCESS(f'{created} medicines created'))

    def _get_unit(self, dosage_form):
        mapping = {
            'tablet': 'tablet',
            'capsule': 'piece',
            'syrup': 'bottle',
            'injection': 'ampoule',
            'cream': 'tube',
            'ointment': 'tube',
            'drops': 'bottle',
            'inhaler': 'inhaler',
            'infusion': 'bottle',
            'solution': 'bottle',
            'suspension': 'bottle',
            'gel': 'tube',
            'lotion': 'bottle',
            'spray': 'bottle',
            'powder': 'sachet',
            'pessary': 'piece',
            'effervescent': 'tablet',
            'lozenge': 'piece',
        }
        return mapping.get(dosage_form, 'piece')
