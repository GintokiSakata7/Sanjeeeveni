class FirstAidStep {
  final int stepNumber;
  final String icon;
  final String instruction;

  FirstAidStep({
    required this.stepNumber,
    required this.icon,
    required this.instruction,
  });

  factory FirstAidStep.fromJson(Map<String, dynamic> json) {
    return FirstAidStep(
      stepNumber: json['step_number'] ?? 0,
      icon: json['icon'] ?? '⚠️',
      instruction: json['instruction'] ?? '',
    );
  }
}

class TriageResult {
  final String severity;
  final String category;
  final String detectedLanguage;
  final String triageSummary;
  final String inputText;
  final String translatedEnglish;
  final String recommendedDoctorSpecialty;
  final List<FirstAidStep> firstAidNative;
  final List<FirstAidStep> firstAidEnglish;

  TriageResult({
    required this.severity,
    required this.category,
    required this.detectedLanguage,
    required this.triageSummary,
    required this.inputText,
    required this.translatedEnglish,
    required this.recommendedDoctorSpecialty,
    required this.firstAidNative,
    required this.firstAidEnglish,
  });

  factory TriageResult.fromJson(Map<String, dynamic> json) {
    List<FirstAidStep> parseSteps(dynamic list) {
      if (list == null) return [];
      return (list as List).map((s) => FirstAidStep.fromJson(s)).toList();
    }

    return TriageResult(
      severity: json['severity'] ?? 'UNKNOWN',
      category: json['category'] ?? 'Unknown',
      detectedLanguage: json['detected_language'] ?? 'unknown',
      triageSummary: json['triage_summary'] ?? '',
      inputText: json['input_text'] ?? '',
      translatedEnglish: json['translated_english'] ?? '',
      recommendedDoctorSpecialty: json['recommended_doctor_specialty'] ?? '',
      firstAidNative: parseSteps(json['first_aid_native']),
      firstAidEnglish: parseSteps(json['first_aid_english']),
    );
  }

  List<FirstAidStep> get primaryFirstAid =>
      firstAidNative.isNotEmpty ? firstAidNative : firstAidEnglish;
}
