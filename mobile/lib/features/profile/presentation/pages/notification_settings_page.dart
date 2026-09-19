import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/storage/token_storage.dart';
import '../../../../core/theme/app_theme.dart';
import '../../data/models/notification_setting_model.dart';
import '../../data/repositories/notification_setting_repository.dart';
import '../../data/services/notification_setting_api_service.dart';

class NotificationSettingsPage extends StatefulWidget {
  const NotificationSettingsPage({super.key});

  @override
  State<NotificationSettingsPage> createState() =>
      _NotificationSettingsPageState();
}

class _NotificationSettingsPageState
    extends State<NotificationSettingsPage> {
  late final NotificationSettingRepository
      _notificationSettingRepository;

  late final TokenStorage _tokenStorage;

  bool _allNotifications = true;
  bool _appointmentNotifications = true;
  bool _medicalRecordNotifications = true;
  bool _systemNotifications = true;

  bool _isLoading = true;
  bool _isSaving = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();

    final apiClient = ApiClient();

    _notificationSettingRepository =
        NotificationSettingRepository(
      apiService:
          NotificationSettingApiService(
        apiClient: apiClient,
      ),
    );

    _tokenStorage = TokenStorage();

    _loadNotificationSettings();
  }

  Future<void> _loadNotificationSettings() async {
    if (!mounted) {
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final userId = await _getUserIdFromToken();

      if (userId == null) {
        throw Exception(
          'ไม่พบข้อมูลผู้ใช้จากบัญชีที่เข้าสู่ระบบ',
        );
      }

      final setting =
          await _notificationSettingRepository
              .getNotificationSettings(
        userId: userId,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        _applySettings(setting);
        _isLoading = false;
      });
    } on DioException catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoading = false;
        _errorMessage =
            _getDioErrorMessage(error);
      });
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoading = false;
        _errorMessage =
            error
                .toString()
                .replaceFirst(
                  'Exception: ',
                  '',
                );
      });
    }
  }

  void _applySettings(
    NotificationSettingModel setting,
  ) {
    _allNotifications =
        setting.allNotifications;
    _appointmentNotifications =
        setting.appointmentNotifications;
    _medicalRecordNotifications =
        setting.medicalRecordNotifications;
    _systemNotifications =
        setting.systemNotifications;
  }

  Future<String?> _getUserIdFromToken() async {
    final accessToken =
        await _tokenStorage.getAccessToken();

    if (accessToken == null ||
        accessToken.isEmpty) {
      return null;
    }

    final parts =
        accessToken.split('.');

    if (parts.length != 3) {
      return null;
    }

    try {
      final payload =
          _decodeJwtPayload(parts[1]);

      final subject =
          payload['sub'];

      if (subject is String &&
          subject.isNotEmpty) {
        return subject;
      }

      return null;
    } catch (_) {
      return null;
    }
  }

  Map<String, dynamic> _decodeJwtPayload(
    String encodedPayload,
  ) {
    final normalized =
        base64Url.normalize(
      encodedPayload,
    );

    final decoded =
        utf8.decode(
      base64Url.decode(
        normalized,
      ),
    );

    final payload =
        jsonDecode(decoded);

    if (payload is! Map) {
      throw const FormatException(
        'Invalid JWT payload',
      );
    }

    return Map<String, dynamic>.from(
      payload,
    );
  }

  Future<void> _updateNotificationSettings({
    required bool allNotifications,
    required bool appointmentNotifications,
    required bool medicalRecordNotifications,
    required bool systemNotifications,
  }) async {
    if (_isSaving) {
      return;
    }

    final userId =
        await _getUserIdFromToken();

    if (userId == null) {
      _showErrorMessage(
        'ไม่พบข้อมูลผู้ใช้จากบัญชีที่เข้าสู่ระบบ',
      );
      return;
    }

    final previousAllNotifications =
        _allNotifications;
    final previousAppointmentNotifications =
        _appointmentNotifications;
    final previousMedicalRecordNotifications =
        _medicalRecordNotifications;
    final previousSystemNotifications =
        _systemNotifications;

    setState(() {
      _allNotifications =
          allNotifications;
      _appointmentNotifications =
          appointmentNotifications;
      _medicalRecordNotifications =
          medicalRecordNotifications;
      _systemNotifications =
          systemNotifications;
      _isSaving = true;
    });

    try {
      final updated =
          await _notificationSettingRepository
              .updateNotificationSettings(
        userId: userId,
        allNotifications:
            allNotifications,
        appointmentNotifications:
            appointmentNotifications,
        medicalRecordNotifications:
            medicalRecordNotifications,
        systemNotifications:
            systemNotifications,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        _applySettings(updated);
        _isSaving = false;
      });
    } on DioException catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _allNotifications =
            previousAllNotifications;
        _appointmentNotifications =
            previousAppointmentNotifications;
        _medicalRecordNotifications =
            previousMedicalRecordNotifications;
        _systemNotifications =
            previousSystemNotifications;
        _isSaving = false;
      });

      _showErrorMessage(
        _getDioErrorMessage(error),
      );
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _allNotifications =
            previousAllNotifications;
        _appointmentNotifications =
            previousAppointmentNotifications;
        _medicalRecordNotifications =
            previousMedicalRecordNotifications;
        _systemNotifications =
            previousSystemNotifications;
        _isSaving = false;
      });

      _showErrorMessage(
        error
            .toString()
            .replaceFirst(
              'Exception: ',
              '',
            ),
      );
    }
  }

  void _showErrorMessage(String message) {
    if (!mounted) {
      return;
    }

    ScaffoldMessenger.of(context)
        .showSnackBar(
      SnackBar(
        content: Text(
          message,
          style: const TextStyle(
            fontFamily: 'Kanit',
          ),
        ),
      ),
    );
  }

  String _getDioErrorMessage(
    DioException error,
  ) {
    final data =
        error.response?.data;

    if (data is Map) {
      final detail =
          data['detail'];

      if (detail is String &&
          detail.isNotEmpty) {
        return detail;
      }
    }

    return 'ไม่สามารถเชื่อมต่อกับระบบได้';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor:
          AppTheme.backgroundColor,
      appBar: AppBar(
        backgroundColor:
            AppTheme.surfaceColor,
        surfaceTintColor:
            Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        leading: IconButton(
          onPressed: () {
            Navigator.of(context).pop();
          },
          icon: const Icon(
            Icons.arrow_back_ios_new_rounded,
            size: 19,
          ),
          color:
              AppTheme.textPrimaryColor,
        ),
        title: const Text(
          'ตั้งค่าการแจ้งเตือน',
          style: TextStyle(
            fontFamily: 'Kanit',
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color:
                AppTheme.textPrimaryColor,
          ),
        ),
        bottom: const PreferredSize(
          preferredSize:
              Size.fromHeight(1),
          child: Divider(
            height: 1,
            thickness: 1,
            color: Color(0xFFE8ECF2),
          ),
        ),
      ),
      body: SafeArea(
        child: _isLoading
            ? const Center(
                child:
                    CircularProgressIndicator(),
              )
            : _errorMessage != null
                ? _buildErrorState()
                : SingleChildScrollView(
                    padding:
                        const EdgeInsets
                            .fromLTRB(
                      20,
                      22,
                      20,
                      40,
                    ),
                    child: Column(
                      crossAxisAlignment:
                          CrossAxisAlignment
                              .start,
                      children: [
                        const Text(
                          'จัดการการแจ้งเตือนที่คุณต้องการรับจาก CareFlow',
                          style:
                              TextStyle(
                            fontFamily:
                                'Kanit',
                            fontSize: 13,
                            fontWeight:
                                FontWeight.w400,
                            color: AppTheme
                                .textSecondaryColor,
                          ),
                        ),
                        const SizedBox(
                          height: 22,
                        ),
                        _buildSectionTitle(
                          'รับการแจ้งเตือน',
                        ),
                        const SizedBox(
                          height: 10,
                        ),
                        _buildMasterNotificationCard(),
                        const SizedBox(
                          height: 20,
                        ),
                        _buildSectionTitle(
                          'การแจ้งเตือน',
                        ),
                        const SizedBox(
                          height: 10,
                        ),
                        _buildNotificationCard(),
                        const SizedBox(
                          height: 24,
                        ),
                        _buildInfoBox(),
                      ],
                    ),
                  ),
      ),
    );
  }

  Widget _buildSectionTitle(
    String title,
  ) {
    return Text(
      title,
      style: const TextStyle(
        fontFamily: 'Kanit',
        fontSize: 15,
        fontWeight: FontWeight.w600,
        color: AppTheme.textPrimaryColor,
      ),
    );
  }

  Widget _buildMasterNotificationCard() {
    return _buildCard(
      padding: EdgeInsets.zero,
      child: _buildNotificationRow(
        icon:
            Icons.notifications_none_rounded,
        iconColor:
            AppTheme.primaryColor,
        iconBackground:
            AppTheme.primaryBackgroundColor,
        title: 'การแจ้งเตือนทั้งหมด',
        description:
            'จัดการการแจ้งเตือนทั้งหมดของคุณ',
        value: _allNotifications,
        onChanged: (value) {
          _updateNotificationSettings(
            allNotifications: value,
            appointmentNotifications:
                value,
            medicalRecordNotifications:
                value,
            systemNotifications:
                value,
          );
        },
      ),
    );
  }

  Widget _buildNotificationCard() {
    return _buildCard(
      padding: EdgeInsets.zero,
      child: Column(
        children: [
          _buildNotificationRow(
            icon:
                Icons.calendar_today_outlined,
            iconColor:
                const Color(0xFF5578D9),
            iconBackground:
                const Color(0xFFE8EEFF),
            title: 'การนัดหมาย',
            description:
                'แจ้งเตือนเกี่ยวกับนัดหมายของคุณ',
            value:
                _appointmentNotifications,
            onChanged: (value) {
              final medicalRecord =
                  _medicalRecordNotifications;
              final system =
                  _systemNotifications;

              final all =
                  value &&
                  medicalRecord &&
                  system;

              _updateNotificationSettings(
                allNotifications: all,
                appointmentNotifications:
                    value,
                medicalRecordNotifications:
                    medicalRecord,
                systemNotifications:
                    system,
              );
            },
          ),
          _buildDivider(),
          _buildNotificationRow(
            icon:
                Icons.medical_information_outlined,
            iconColor:
                const Color(0xFF35A85A),
            iconBackground:
                const Color(0xFFE5F9EA),
            title: 'ผลการรักษา',
            description:
                'แจ้งเตือนเมื่อมีข้อมูลการรักษาใหม่',
            value:
                _medicalRecordNotifications,
            onChanged: (value) {
              final appointment =
                  _appointmentNotifications;
              final system =
                  _systemNotifications;

              final all =
                  appointment &&
                  value &&
                  system;

              _updateNotificationSettings(
                allNotifications: all,
                appointmentNotifications:
                    appointment,
                medicalRecordNotifications:
                    value,
                systemNotifications:
                    system,
              );
            },
          ),
          _buildDivider(),
          _buildNotificationRow(
            icon:
                Icons.info_outline_rounded,
            iconColor:
                const Color(0xFF8A63D2),
            iconBackground:
                const Color(0xFFF0EAFE),
            title: 'การแจ้งเตือนระบบ',
            description:
                'ข่าวสารและข้อมูลสำคัญจากระบบ',
            value:
                _systemNotifications,
            onChanged: (value) {
              final appointment =
                  _appointmentNotifications;
              final medicalRecord =
                  _medicalRecordNotifications;

              final all =
                  appointment &&
                  medicalRecord &&
                  value;

              _updateNotificationSettings(
                allNotifications: all,
                appointmentNotifications:
                    appointment,
                medicalRecordNotifications:
                    medicalRecord,
                systemNotifications:
                    value,
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationRow({
    required IconData icon,
    required Color iconColor,
    required Color iconBackground,
    required String title,
    required String description,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Padding(
      padding:
          const EdgeInsets.symmetric(
        horizontal: 15,
        vertical: 14,
      ),
      child: Row(
        crossAxisAlignment:
            CrossAxisAlignment.center,
        children: [
          Container(
            width: 36,
            height: 36,
            decoration:
                BoxDecoration(
              color: iconBackground,
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              size: 19,
              color: iconColor,
            ),
          ),
          const SizedBox(
            width: 12,
          ),
          Expanded(
            child: Column(
              mainAxisAlignment:
                  MainAxisAlignment.center,
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  maxLines: 1,
                  overflow:
                      TextOverflow.ellipsis,
                  style:
                      const TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 13,
                    fontWeight:
                        FontWeight.w500,
                    color: AppTheme
                        .textPrimaryColor,
                  ),
                ),
                const SizedBox(
                  height: 2,
                ),
                Text(
                  description,
                  maxLines: 1,
                  overflow:
                      TextOverflow.ellipsis,
                  style:
                      const TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 10,
                    fontWeight:
                        FontWeight.w400,
                    height: 1.35,
                    color: AppTheme
                        .textSecondaryColor,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(
            width: 8,
          ),
          SizedBox(
            width: 42,
            child: Align(
              alignment:
                  Alignment.centerRight,
              child: Transform.scale(
                scale: 0.82,
                child: Switch.adaptive(
                  value: value,
                  onChanged:
                      _isSaving
                          ? null
                          : onChanged,
                  activeTrackColor:
                      AppTheme.primaryColor,
                  inactiveTrackColor:
                      const Color(
                    0xFFD9DDE3,
                  ),
                  inactiveThumbColor:
                      Colors.white,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDivider() {
    return const Padding(
      padding:
          EdgeInsets.only(left: 63),
      child: Divider(
        height: 1,
        thickness: 1,
        color: Color(0xFFE9EDF2),
      ),
    );
  }

  Widget _buildInfoBox() {
    return Container(
      width: double.infinity,
      padding:
          const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color:
            AppTheme.primaryBackgroundColor,
        borderRadius:
            BorderRadius.circular(12),
      ),
      child: const Row(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.info_outline_rounded,
            size: 18,
            color: AppTheme.primaryColor,
          ),
          SizedBox(
            width: 8,
          ),
          Expanded(
            child: Text(
              'คุณสามารถเปิดหรือปิดการแจ้งเตือนแต่ละประเภทได้ตามต้องการ',
              style:
                  TextStyle(
                fontFamily: 'Kanit',
                fontSize: 11,
                fontWeight:
                    FontWeight.w400,
                height: 1.4,
                color: AppTheme
                    .textSecondaryColor,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Padding(
        padding:
            const EdgeInsets.symmetric(
          horizontal: 32,
        ),
        child: Column(
          mainAxisAlignment:
              MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline_rounded,
              size: 48,
              color:
                  AppTheme.textSecondaryColor,
            ),
            const SizedBox(
              height: 14,
            ),
            const Text(
              'ไม่สามารถโหลดการตั้งค่าการแจ้งเตือนได้',
              textAlign:
                  TextAlign.center,
              style:
                  TextStyle(
                fontFamily: 'Kanit',
                fontSize: 16,
                fontWeight:
                    FontWeight.w500,
                color: AppTheme
                    .textPrimaryColor,
              ),
            ),
            const SizedBox(
              height: 8,
            ),
            Text(
              _errorMessage ??
                  'กรุณาลองใหม่อีกครั้ง',
              textAlign:
                  TextAlign.center,
              style:
                  const TextStyle(
                fontFamily: 'Kanit',
                fontSize: 12,
                color: AppTheme
                    .textSecondaryColor,
              ),
            ),
            const SizedBox(
              height: 18,
            ),
            ElevatedButton(
              onPressed:
                  _loadNotificationSettings,
              child: const Text(
                'ลองใหม่',
                style:
                    TextStyle(
                  fontFamily: 'Kanit',
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCard({
    required Widget child,
    EdgeInsetsGeometry padding =
        const EdgeInsets.all(15),
  }) {
    return Container(
      width: double.infinity,
      padding: padding,
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius:
            BorderRadius.circular(17),
        border: Border.all(
          color: AppTheme
              .textSecondaryColor
              .withValues(alpha: 0.08),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.white
                .withValues(alpha: 0.9),
            blurRadius: 6,
            offset:
                const Offset(0, -2),
          ),
          BoxShadow(
            color: Colors.black
                .withValues(alpha: 0.035),
            blurRadius: 10,
            offset:
                const Offset(0, 3),
          ),
        ],
      ),
      child: child,
    );
  }
}