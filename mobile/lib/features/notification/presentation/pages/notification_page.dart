import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/storage/token_storage.dart';
import '../../../../core/theme/app_theme.dart';
import '../../data/models/notification_model.dart';
import '../../data/repositories/notification_repository.dart';
import '../../data/services/notification_api_service.dart';

class _NoStretchScrollBehavior extends ScrollBehavior {
  const _NoStretchScrollBehavior();

  @override
  ScrollPhysics getScrollPhysics(BuildContext context) {
    return const ClampingScrollPhysics();
  }
}

class NotificationPage extends StatefulWidget {
  const NotificationPage({super.key});

  @override
  State<NotificationPage> createState() => _NotificationPageState();
}

class _NotificationPageState extends State<NotificationPage> {
  late final NotificationRepository _notificationRepository;

  late final TokenStorage _tokenStorage;

  String _selectedFilter = 'ทั้งหมด';

  List<NotificationModel> _notifications = [];

  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();

    final apiClient = ApiClient();

    _notificationRepository = NotificationRepository(
      apiService: NotificationApiService(apiClient: apiClient),
    );

    _tokenStorage = TokenStorage();

    _loadNotifications();
  }

  Future<void> _loadNotifications() async {
    if (!mounted) {
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final patientId = await _getPatientIdFromToken();

      if (patientId == null) {
        throw Exception('ไม่พบข้อมูลผู้ป่วยจากบัญชีที่เข้าสู่ระบบ');
      }

      final notifications = await _notificationRepository
          .getPatientNotifications(patientId: patientId);

      if (!mounted) {
        return;
      }

      setState(() {
        _notifications = notifications;
        _isLoading = false;
      });
    } on DioException catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoading = false;
        _errorMessage = _getDioErrorMessage(error);
      });
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoading = false;
        _errorMessage = error.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  Future<String?> _getPatientIdFromToken() async {
    final accessToken = await _tokenStorage.getAccessToken();

    if (accessToken == null || accessToken.isEmpty) {
      return null;
    }

    final parts = accessToken.split('.');

    if (parts.length != 3) {
      return null;
    }

    try {
      final payload = _decodeJwtPayload(parts[1]);

      final subject = payload['sub'];

      if (subject is String && subject.isNotEmpty) {
        return subject;
      }

      return null;
    } catch (_) {
      return null;
    }
  }

  Map<String, dynamic> _decodeJwtPayload(String encodedPayload) {
    final normalized = base64Url.normalize(encodedPayload);

    final decoded = utf8.decode(base64Url.decode(normalized));

    final payload = jsonDecode(decoded);

    if (payload is! Map) {
      throw const FormatException('Invalid JWT payload');
    }

    return Map<String, dynamic>.from(payload);
  }

  List<NotificationModel> _getFilteredNotifications() {
    switch (_selectedFilter) {
      case 'นัดหมาย':
        return _notifications
            .where((notification) => _isAppointmentNotification(notification))
            .toList();

      case 'ทั้งหมด':
      default:
        return List<NotificationModel>.from(_notifications);
    }
  }

  bool _isAppointmentNotification(NotificationModel notification) {
    switch (notification.type) {
      case NotificationType.appointmentConfirmed:
      case NotificationType.reminder3Days:
      case NotificationType.reminder1Day:
      case NotificationType.reminder30Minutes:
      case NotificationType.readyForConsultation:
      case NotificationType.consultationDelayed:
      case NotificationType.appointmentCancelled:
      case NotificationType.appointmentRescheduled:
        return true;
    }
  }

  @override
  Widget build(BuildContext context) {
    final notifications = _getFilteredNotifications();

    final todayNotifications = notifications
        .where((item) => _isToday(item.createdAt))
        .toList();

    final previousNotifications = notifications
        .where((item) => !_isToday(item.createdAt))
        .toList();

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        backgroundColor: AppTheme.surfaceColor,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        leading: IconButton(
          onPressed: () {
            Navigator.of(context).pop();
          },
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
          color: AppTheme.textPrimaryColor,
        ),
        title: const Text(
          'การแจ้งเตือน',
          style: TextStyle(
            fontFamily: 'Kanit',
            fontSize: 21,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            _buildFilterSection(),
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _errorMessage != null
                  ? _buildErrorState()
                  : notifications.isEmpty
                  ? _buildEmptyState()
                  : ScrollConfiguration(
                      behavior: const _NoStretchScrollBehavior(),
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.fromLTRB(18, 12, 18, 32),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (todayNotifications.isNotEmpty) ...[
                              _buildSectionTitle('วันนี้'),
                              const SizedBox(height: 10),
                              for (final notification in todayNotifications)
                                _buildNotificationCard(notification),
                            ],
                            if (todayNotifications.isNotEmpty &&
                                previousNotifications.isNotEmpty)
                              const SizedBox(height: 8),
                            if (previousNotifications.isNotEmpty) ...[
                              _buildSectionTitle('ก่อนหน้านี้'),
                              const SizedBox(height: 10),
                              for (final notification in previousNotifications)
                                _buildNotificationCard(notification),
                            ],
                          ],
                        ),
                      ),
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterSection() {
    const filters = ['ทั้งหมด', 'นัดหมาย'];

    return Container(
      width: double.infinity,
      color: AppTheme.surfaceColor,
      padding: const EdgeInsets.fromLTRB(18, 4, 18, 14),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            for (final filter in filters)
              Padding(
                padding: const EdgeInsets.only(right: 9),
                child: GestureDetector(
                  onTap: () {
                    setState(() {
                      _selectedFilter = filter;
                    });
                  },
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 18,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: _selectedFilter == filter
                          ? AppTheme.primaryColor
                          : const Color(0xFFEDEDEF),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      filter,
                      style: TextStyle(
                        fontFamily: 'Kanit',
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                        color: _selectedFilter == filter
                            ? Colors.white
                            : AppTheme.textSecondaryColor,
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontFamily: 'Kanit',
        fontSize: 15,
        fontWeight: FontWeight.w500,
        color: AppTheme.textPrimaryColor,
      ),
    );
  }

  Widget _buildNotificationCard(NotificationModel notification) {
    final iconData = _getNotificationIcon(notification.type);

    final iconColor = _getNotificationIconColor(notification.type);

    final iconBackground = _getNotificationIconBackground(notification.type);

    return GestureDetector(
      onTap: () async {
        await _markAsRead(notification);

        if (!mounted) {
          return;
        }

        await _showNotificationDialog(notification);
      },
      child: Container(
        width: double.infinity,
        margin: const EdgeInsets.only(bottom: 11),
        padding: const EdgeInsets.fromLTRB(13, 14, 14, 14),
        decoration: BoxDecoration(
          color: AppTheme.surfaceColor,
          borderRadius: BorderRadius.circular(16),
          border: notification.isRead
              ? null
              : Border(
                  left: BorderSide(color: AppTheme.primaryColor, width: 3),
                ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.045),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 43,
              height: 43,
              decoration: BoxDecoration(
                color: iconBackground,
                shape: BoxShape.circle,
              ),
              child: Icon(iconData, size: 21, color: iconColor),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Text(
                          notification.title,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            fontFamily: 'Kanit',
                            fontSize: 14,
                            fontWeight: notification.isRead
                                ? FontWeight.w500
                                : FontWeight.w600,
                            color: AppTheme.textPrimaryColor,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        _formatRelativeTime(notification.createdAt),
                        style: const TextStyle(
                          fontFamily: 'Kanit',
                          fontSize: 10,
                          fontWeight: FontWeight.w400,
                          color: AppTheme.textSecondaryColor,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 5),
                  Text(
                    notification.body,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontFamily: 'Kanit',
                      fontSize: 11,
                      fontWeight: FontWeight.w400,
                      height: 1.45,
                      color: AppTheme.textSecondaryColor,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _markAsRead(NotificationModel notification) async {
    if (notification.isRead) {
      return;
    }

    try {
      final updated = await _notificationRepository.markNotificationAsRead(
        notificationId: notification.id,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        final index = _notifications.indexWhere(
          (item) => item.id == notification.id,
        );

        if (index != -1) {
          _notifications[index] = updated;
        }
      });
    } on DioException {
      // Keep the notification visible
      // even if marking as read fails.
    }
  }

  Future<void> _showNotificationDialog(NotificationModel notification) async {
    final iconData = _getNotificationIcon(notification.type);

    final iconColor = _getNotificationIconColor(notification.type);

    final iconBackground = _getNotificationIconBackground(notification.type);

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return Dialog(
          backgroundColor: Colors.transparent,
          insetPadding: const EdgeInsets.symmetric(horizontal: 40),
          child: Container(
            padding: const EdgeInsets.fromLTRB(20, 22, 20, 18),
            decoration: BoxDecoration(
              color: const Color(0xFFF8F8FC),
              borderRadius: BorderRadius.circular(24),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 58,
                  height: 58,
                  decoration: BoxDecoration(
                    color: iconBackground,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(iconData, size: 29, color: iconColor),
                ),

                const SizedBox(height: 17),

                Text(
                  notification.title,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),

                const SizedBox(height: 8),

                _buildDialogNotificationBody(notification.body),

                const SizedBox(height: 8),

                Text(
                  _formatDateTime(notification.createdAt),
                  style: const TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 10,
                    color: AppTheme.textSecondaryColor,
                  ),
                ),

                const SizedBox(height: 20),

                SizedBox(
                  width: double.infinity,
                  height: 44,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                    },
                    style: ElevatedButton.styleFrom(
                      elevation: 0,
                      backgroundColor: AppTheme.primaryColor,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(22),
                      ),
                    ),
                    child: const Text(
                      'ตกลง',
                      style: TextStyle(
                        fontFamily: 'Kanit',
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildDialogNotificationBody(String body) {
    final dateIndex = body.indexOf('วันที่');

    if (dateIndex == -1) {
      return Text(
        body,
        textAlign: TextAlign.center,
        style: const TextStyle(
          fontFamily: 'Kanit',
          fontSize: 13,
          fontWeight: FontWeight.w400,
          height: 1.45,
          color: AppTheme.textSecondaryColor,
        ),
      );
    }

    final message = body.substring(0, dateIndex).trim();

    final appointmentDateTime = body.substring(dateIndex).trim();

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          message,
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontFamily: 'Kanit',
            fontSize: 13,
            fontWeight: FontWeight.w400,
            height: 1.45,
            color: AppTheme.textSecondaryColor,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          appointmentDateTime,
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontFamily: 'Kanit',
            fontSize: 13,
            fontWeight: FontWeight.w500,
            height: 1.45,
            color: AppTheme.textPrimaryColor,
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 72,
            height: 72,
            decoration: const BoxDecoration(
              color: Color(0xFFEFF1F5),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.notifications_none_rounded,
              size: 34,
              color: AppTheme.textSecondaryColor,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'ไม่มีการแจ้งเตือน',
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 17,
              fontWeight: FontWeight.w500,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'ยังไม่มีการแจ้งเตือนในหมวดหมู่นี้',
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 12,
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline_rounded,
              size: 48,
              color: AppTheme.textSecondaryColor,
            ),
            const SizedBox(height: 14),
            const Text(
              'ไม่สามารถโหลดการแจ้งเตือนได้',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontFamily: 'Kanit',
                fontSize: 16,
                fontWeight: FontWeight.w500,
                color: AppTheme.textPrimaryColor,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _errorMessage ?? 'กรุณาลองใหม่อีกครั้ง',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontFamily: 'Kanit',
                fontSize: 12,
                color: AppTheme.textSecondaryColor,
              ),
            ),
            const SizedBox(height: 18),
            ElevatedButton(
              onPressed: _loadNotifications,
              child: const Text(
                'ลองใหม่',
                style: TextStyle(fontFamily: 'Kanit'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  bool _isToday(DateTime date) {
    final now = DateTime.now();

    return date.year == now.year &&
        date.month == now.month &&
        date.day == now.day;
  }

  String _formatRelativeTime(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.isNegative) {
      return 'เมื่อสักครู่';
    }

    if (difference.inMinutes < 1) {
      return 'เมื่อสักครู่';
    }

    if (difference.inMinutes < 60) {
      return '${difference.inMinutes} นาทีที่แล้ว';
    }

    if (difference.inHours < 24) {
      return '${difference.inHours} ชม. ที่แล้ว';
    }

    if (difference.inDays < 7) {
      return '${difference.inDays} วันที่แล้ว';
    }

    return _formatDateTime(date);
  }

  String _formatDateTime(DateTime date) {
    final day = date.day.toString().padLeft(2, '0');

    final month = date.month.toString().padLeft(2, '0');

    final year = date.year + 543;

    final hour = date.hour.toString().padLeft(2, '0');

    final minute = date.minute.toString().padLeft(2, '0');

    return '$day/$month/$year $hour:$minute น.';
  }

  IconData _getNotificationIcon(NotificationType type) {
    switch (type) {
      case NotificationType.appointmentConfirmed:
        return Icons.calendar_month_rounded;

      case NotificationType.appointmentCancelled:
        return Icons.event_busy_rounded;

      case NotificationType.reminder3Days:
      case NotificationType.reminder1Day:
      case NotificationType.reminder30Minutes:
        return Icons.access_time_rounded;

      case NotificationType.readyForConsultation:
        return Icons.medical_services_rounded;

      case NotificationType.consultationDelayed:
        return Icons.schedule_rounded;

      case NotificationType.appointmentRescheduled:
        return Icons.event_repeat_rounded;
    }
  }

  Color _getNotificationIconColor(NotificationType type) {
    switch (type) {
      case NotificationType.appointmentCancelled:
      case NotificationType.consultationDelayed:
        return const Color(0xFFE08A27);

      case NotificationType.readyForConsultation:
        return const Color(0xFF35A85A);

      case NotificationType.appointmentConfirmed:
      case NotificationType.reminder3Days:
      case NotificationType.reminder1Day:
      case NotificationType.reminder30Minutes:
      case NotificationType.appointmentRescheduled:
        return const Color(0xFF365ED8);
    }
  }

  Color _getNotificationIconBackground(NotificationType type) {
    switch (type) {
      case NotificationType.appointmentCancelled:
      case NotificationType.consultationDelayed:
        return const Color(0xFFFFEBD6);

      case NotificationType.readyForConsultation:
        return const Color(0xFFE4F8E9);

      case NotificationType.appointmentConfirmed:
      case NotificationType.reminder3Days:
      case NotificationType.reminder1Day:
      case NotificationType.reminder30Minutes:
      case NotificationType.appointmentRescheduled:
        return const Color(0xFFE8EEFF);
    }
  }

  String _getDioErrorMessage(DioException error) {
    final data = error.response?.data;

    if (data is Map) {
      final detail = data['detail'];

      if (detail is String && detail.isNotEmpty) {
        return detail;
      }
    }

    return 'ไม่สามารถเชื่อมต่อกับระบบได้';
  }
}
