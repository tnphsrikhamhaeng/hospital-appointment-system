import 'package:flutter/foundation.dart';

@immutable
class MedicalRecordModel {
  const MedicalRecordModel({
    required this.id,
    required this.appointmentId,
    required this.patientId,
    required this.doctorId,
    required this.chiefComplaint,
    required this.diagnosis,
    this.presentIllness,
    this.physicalExamination,
    this.treatment,
    this.recommendation,
    this.note,
    required this.createdAt,
    required this.updatedAt,
  });

  final String id;
  final String appointmentId;
  final String patientId;
  final String doctorId;

  final String chiefComplaint;
  final String? presentIllness;
  final String? physicalExamination;
  final String diagnosis;
  final String? treatment;
  final String? recommendation;
  final String? note;

  final DateTime createdAt;
  final DateTime updatedAt;

  factory MedicalRecordModel.fromJson(
    Map<String, dynamic> json,
  ) {
    return MedicalRecordModel(
      id: json['id'] as String,
      appointmentId: json['appointment_id'] as String,
      patientId: json['patient_id'] as String,
      doctorId: json['doctor_id'] as String,
      chiefComplaint: json['chief_complaint'] as String,
      presentIllness: json['present_illness'] as String?,
      physicalExamination:
          json['physical_examination'] as String?,
      diagnosis: json['diagnosis'] as String,
      treatment: json['treatment'] as String?,
      recommendation: json['recommendation'] as String?,
      note: json['note'] as String?,
      createdAt: DateTime.parse(
        json['created_at'] as String,
      ),
      updatedAt: DateTime.parse(
        json['updated_at'] as String,
      ),
    );
  }
}