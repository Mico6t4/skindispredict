from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from .models import PredictionResult
from .forms import PredictionResultForm
from .utils import predict_image
import os

def home(request):
    return render(request, 'predictions/home.html')

def result_list(request):
    search_query = request.GET.get('search', '')
    results = PredictionResult.objects.all().order_by('-created_at')
    
    if search_query:
        results = results.filter(Q(predicted_class__icontains=search_query))
    
    paginator = Paginator(results, 10)  # Show 10 results per page
    page = request.GET.get('page')
    
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    
    return render(request, 'predictions/result_list.html', {'results': results})

def result_edit(request, pk):
    result = get_object_or_404(PredictionResult, pk=pk)
    if request.method == 'POST':
        form = PredictionResultForm(request.POST, request.FILES, instance=result)
        if form.is_valid():
            if 'image' in request.FILES:
                # Save the new image
                new_image = request.FILES['image']
                fs = FileSystemStorage(location='media/analyzed_images/')
                filename = fs.save(new_image.name, new_image)
                uploaded_file_url = fs.url(filename)
                
                # Run prediction on the new image
                image_path = os.path.join('media/analyzed_images', filename)
                predicted_class, confidence = predict_image(image_path)
                
                # Update the result object
                result.image = 'analyzed_images/' + filename
                result.predicted_class = predicted_class
                result.confidence = confidence * 100
                
                # Update diagnosis and treatment based on the new prediction
                result.diagnosis = get_diagnosis(predicted_class)
                result.treatment = get_treatment(predicted_class)
            
            result.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            
            messages.success(request, 'Changes saved successfully!')
            return redirect('result_detail', pk=pk)
    else:
        form = PredictionResultForm(instance=result)
    return render(request, 'predictions/result_edit.html', {'form': form, 'result': result})

def result_delete(request, pk):
    result = get_object_or_404(PredictionResult, pk=pk)
    if request.method == 'POST':
        result.delete()
        return redirect('result_list')
    return render(request, 'predictions/result_delete.html', {'result': result})

def get_diagnosis(predicted_class):
    # Add your diagnosis logic here based on the predicted class
    diagnoses = {
        'BA- cellulitis': "Cellulitis is a bacterial infection of the skin and underlying tissue.",
        'BA-impetigo': "Impetigo is a highly contagious bacterial skin infection.",
        'FU-athlete-foot': "Athlete's foot is a common fungal infection that affects the skin on the feet.",
        'FU-nail-fungus': "Nail fungus is a common condition that begins as a white or yellow spot under the tip of your fingernail or toenail.",
        'FU-ringworm': "Ringworm is a common fungal skin infection characterized by a red, circular rash.",
        'PA-cutaneous-larva-migrans': "Cutaneous Larva Migrans is a skin condition caused by hookworm larvae penetrating the epidermis.",
        'VI-chickenpox': "Chickenpox is a highly contagious viral infection causing an itchy, blister-like rash on the skin."
    }
    return diagnoses.get(predicted_class, "No specific diagnosis available for this condition.")

def get_treatment(predicted_class):
    # Add your treatment logic here based on the predicted class
    treatments = {
        'BA- cellulitis': "Treatment typically involves oral antibiotics. In severe cases, intravenous antibiotics may be necessary.",
        'BA-impetigo': "Treatment usually consists of antibiotic ointments or oral antibiotics.",
        'FU-athlete-foot': "Over-the-counter antifungal creams, sprays, or powders are often effective.",
        'FU-nail-fungus': "Treatment options include oral antifungal drugs, medicated nail polish, or topical solutions.",
        'FU-ringworm': "Antifungal creams, lotions, or powders are typically used for treatment.",
        'PA-cutaneous-larva-migrans': "Treatment usually involves antiparasitic medications such as albendazole or ivermectin.",
        'VI-chickenpox': "Treatment focuses on relieving symptoms, including calamine lotion for itching and acetaminophen for fever."
    }
    return treatments.get(predicted_class, "Consult a healthcare professional for appropriate treatment options.")

def result_detail(request, pk):
    result = get_object_or_404(PredictionResult, pk=pk)
    return render(request, 'predictions/result.html', {'result': result})

def upload_image(request):
    if request.method == 'POST':
        form = PredictionResultForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded image
            uploaded_image = request.FILES['image']
            fs = FileSystemStorage(location='media/analyzed_images/')
            filename = fs.save(uploaded_image.name, uploaded_image)
            uploaded_file_url = fs.url(filename)

            # Run prediction on the uploaded image
            image_path = os.path.join('media/analyzed_images', filename)
            predicted_class, confidence = predict_image(image_path)

            # Create and save the prediction result
            result = form.save(commit=False)
            result.image = 'analyzed_images/' + filename  # Store relative path
            result.predicted_class = predicted_class
            result.confidence = confidence * 100
            result.diagnosis = get_diagnosis(predicted_class)
            result.treatment = get_treatment(predicted_class)
            result.save()

            return redirect('result_detail', pk=result.pk)
    else:
        form = PredictionResultForm()

    return render(request, 'predictions/upload.html', {'form': form})

# ... (keep all existing functions)

def common_symptoms(request, condition):
    symptoms = {
        'BA- cellulitis': [
            "Redness and swelling of the affected area",
            "Warmth and tenderness to touch",
            "Fever and chills",
            "Skin dimpling or pitting",
            "Swollen lymph nodes"
        ],
        'BA-impetigo': [
            "Red sores that quickly rupture, ooze for a few days and then form a yellowish-brown crust",
            "Itchy rash",
            "Fluid-filled blisters",
            "Typically appears around the nose and mouth"
        ],
        'FU-athlete-foot': [
            "Itching, stinging, and burning between the toes",
            "Itchy blisters on feet",
            "Cracking and peeling skin on feet, especially between the toes and on the soles",
            "Dry skin on the sides or soles of feet",
            "Raw skin on the feet"
        ],
        'FU-nail-fungus': [
            "Thickened nails",
            "Whitish to yellow-brown discoloration",
            "Brittle, crumbly or ragged nails",
            "Distorted nail shape",
            "Dark color, caused by debris building up under your nail"
        ],
        'FU-ringworm': [
            "Red, scaly, itchy patch on the skin",
            "Slightly raised, expanding ring on the skin",
            "A round, flat patch of itchy skin",
            "Overlapping rings on the skin"
        ],
        'PA-cutaneous-larva-migrans': [
            "Intensely itchy, raised tracks on the skin",
            "Tracks appear as reddish-brown, wavy lines",
            "Most common on feet, legs, and buttocks",
            "Tracks may move 1-2 cm per day"
        ],
        'VI-chickenpox': [
            "Itchy, fluid-filled blisters",
            "Fever",
            "Fatigue and loss of appetite",
            "Headache",
            "Rash that turns into itchy, fluid-filled blisters that eventually turn into scabs"
        ]
    }
    
    context = {
        'condition': condition,
        'symptoms': symptoms.get(condition, ["No specific symptoms available for this condition."]),
        'result_id': request.GET.get('result_id')
    }
    return render(request, 'predictions/common_symptoms.html', context)

def prevention_tips(request, condition):
    tips = {
        'BA- cellulitis': [
            "Practice good hygiene and wash your hands regularly",
            "Clean any cuts or wounds promptly",
            "Apply moisturizer to dry, cracked skin",
            "Wear appropriate protective gear when working or playing sports",
            "Manage underlying conditions like diabetes or eczema"
        ],
        'BA-impetigo': [
            "Practice good hygiene and wash hands frequently",
            "Keep cuts, scrapes, and insect bites clean and covered",
            "Avoid sharing personal items like towels or clothes",
            "Cut fingernails short and keep them clean",
            "Wash an infected person's clothes, towels, and bedding daily"
        ],
        'FU-athlete-foot': [
            "Keep feet dry, especially between toes",
            "Change socks regularly, especially if feet get sweaty",
            "Wear sandals in public showers or locker rooms",
            "Don't share shoes or socks with others",
            "Alternate pairs of shoes daily to allow them to dry"
        ],
        'FU-nail-fungus': [
            "Keep hands and feet clean and dry",
            "Wear sweat-absorbing socks",
            "Choose shoes made of materials that breathe",
            "Discard old shoes or treat them with disinfectants or antifungal powders",
            "Don't go barefoot in public areas"
        ],
        'FU-ringworm': [
            "Keep skin clean and dry",
            "Don't walk barefoot in public areas",
            "Don't share personal items like clothing or towels",
            "Wash hands often",
            "Take your pet to the vet if it has patches of missing fur"
        ],
        'PA-cutaneous-larva-migrans': [
            "Avoid walking barefoot on beaches or in areas where there may be animal feces",
            "Lie on a towel or mat when on the beach",
            "Wash hands thoroughly after handling soil or sand",
            "Deworm pets regularly",
            "Practice good sanitation and hygiene in areas where hookworms are common"
        ],
        'VI-chickenpox': [
            "Get vaccinated against chickenpox",
            "Avoid close contact with people who have chickenpox",
            "Practice good hygiene, including regular hand washing",
            "Strengthen your immune system through a healthy diet and lifestyle",
            "If exposed, consult a doctor about potential preventive treatments"
        ]
    }
    
    context = {
        'condition': condition,
        'prevention_tips': tips.get(condition, ["No specific prevention tips available for this condition."]),
        'result_id': request.GET.get('result_id')
    }
    return render(request, 'predictions/prevention_tips.html', context)

def when_to_see_doctor(request, condition):
    warning_signs = {
        'BA- cellulitis': [
            "The affected area is warm to the touch and painful",
            "The redness or swelling spreads rapidly",
            "You develop a fever",
            "The skin starts to blister or develop red streaks",
            "You have a weakened immune system"
        ],
        'BA-impetigo': [
            "The sores are spreading or getting worse",
            "The rash doesn't improve after a few days",
            "You develop a fever",
            "The area becomes red, warm, and tender (signs of cellulitis)",
            "You have a weakened immune system"
        ],
        'FU-athlete-foot': [
            "The rash doesn't improve after self-treatment",
            "You have diabetes and suspect athlete's foot",
            "You notice excessive redness, swelling, drainage or fever",
            "The infection appears to be spreading to your nails",
            "You have a weakened immune system"
        ],
        'FU-nail-fungus': [
            "Over-the-counter treatments haven't helped",
            "Your nails become painful",
            "You have diabetes and think you're developing nail fungus",
            "The nail infection appears severe or is spreading to other nails",
            "You have a weakened immune system"
        ],
        'FU-ringworm': [
            "The rash doesn't improve after two weeks of self-treatment",
            "The rash spreads to your face or scalp",
            "You develop a fever or pus-filled sores",
            "The affected area becomes painful or starts oozing",
            "You have a weakened immune system"
        ],
        'PA-cutaneous-larva-migrans': [
            "The rash persists or worsens after a few weeks",
            "You develop a fever",
            "The affected area becomes red, warm, and painful",
            "You experience persistent itching that interferes with daily activities or sleep",
            "You have a weakened immune system"
        ],
        'VI-chickenpox': [
            "You develop a high fever that persists",
            "The rash spreads to one or both eyes",
            "The rash gets very red, warm or tender (signs of secondary bacterial infection)",
            "You experience dizziness, disorientation, rapid heartbeat, shortness of breath, tremors, loss of muscle coordination, worsening cough, vomiting, stiff neck or fever lasting longer than four days",
            "You have a weakened immune system or are pregnant"
        ]
    }
    
    context = {
        'condition': condition,
        'warning_signs': warning_signs.get(condition, ["If you have any concerns about your condition, it's always best to consult with a healthcare professional."]),
        'result_id': request.GET.get('result_id')
    }
    return render(request, 'predictions/when_to_see_doctor.html', context)

def result_detail(request, pk):
    result = get_object_or_404(PredictionResult, pk=pk)
    context = {
        'result': result,
        'common_symptoms_url': f"/predictions/common_symptoms/{result.predicted_class}/?result_id={result.id}",
        'prevention_tips_url': f"/predictions/prevention_tips/{result.predicted_class}/?result_id={result.id}",
        'when_to_see_doctor_url': f"/predictions/when_to_see_doctor/{result.predicted_class}/?result_id={result.id}",
    }
    return render(request, 'predictions/result.html', context)