from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html, mark_safe
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from core.models import User, Vendor, Collector, Product, FraudFlag

# ============================================
# CUSTOM FILTERS
# ============================================

class UserTypeListFilter(admin.SimpleListFilter):
    title = _('user type')
    parameter_name = 'user_type'
    
    def lookups(self, request, model_admin):
        return (
            ('customer', _('👤 Customers')),
            ('vendor', _('🏪 Vendors')),
            ('collector', _('🚚 Collectors')),
            ('admin', _('⚙️ Admins')),
        )
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_type=self.value())
        return queryset

class VendorStatusFilter(admin.SimpleListFilter):
    title = _('verification status')
    parameter_name = 'verification_status'
    
    def lookups(self, request, model_admin):
        return (
            ('pending', _('⏳ Pending Review')),
            ('under_review', _('🔍 Under Review')),
            ('approved', _('✅ Approved')),
            ('rejected', _('❌ Rejected')),
            ('suspended', _('🚫 Suspended')),
        )
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(verification_status=self.value())
        return queryset

class TrustScoreFilter(admin.SimpleListFilter):
    title = _('trust score')
    parameter_name = 'trust_score_range'
    
    def lookups(self, request, model_admin):
        return (
            ('90-100', _('🟢 Excellent (90-100)')),
            ('70-89', _('🟡 Good (70-89)')),
            ('50-69', _('🟠 Average (50-69)')),
            ('below50', _('🔴 Poor (<50)')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == '90-100':
            return queryset.filter(trust_score__gte=90)
        elif self.value() == '70-89':
            return queryset.filter(trust_score__gte=70, trust_score__lt=90)
        elif self.value() == '50-69':
            return queryset.filter(trust_score__gte=50, trust_score__lt=70)
        elif self.value() == 'below50':
            return queryset.filter(trust_score__lt=50)
        return queryset

# ============================================
# USER ADMIN
# ============================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'get_full_name', 'user_type_badge', 'wallet_balance', 'loyalty_points', 'is_active', 'date_joined']
    list_filter = [UserTypeListFilter, 'is_active', 'is_email_verified', 'date_joined']
    search_fields = ['email', 'phone', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {
            'fields': ('first_name', 'last_name', 'phone', 'address', 'city', 'state', 'pincode')
        }),
        (_('Location'), {'fields': ('latitude', 'longitude')}),
        (_('Financial'), {'fields': ('wallet_balance', 'loyalty_points')}),
        (_('Status & Permissions'), {
            'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2', 'user_type'),
        }),
    )
    
    actions = ['activate_users', 'deactivate_users']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Name'
    
    def user_type_badge(self, obj):
        colors = {
            'customer': '#4299e1',  # blue
            'vendor': '#48bb78',     # green
            'collector': '#ed8936',  # orange
            'admin': '#e53e3e'       # red
        }
        icons = {
            'customer': '👤',
            'vendor': '🏪',
            'collector': '🚚',
            'admin': '⚙️'
        }
        color = colors.get(obj.user_type, 'gray')
        icon = icons.get(obj.user_type, '')
        return format_html('<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.85em;">{} {}</span>', 
                          color, icon, obj.get_user_type_display())
    user_type_badge.short_description = 'Type'
    
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        messages.success(request, f'{queryset.count()} users activated.')
    activate_users.short_description = "✅ Activate selected users"
    
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        messages.success(request, f'{queryset.count()} users deactivated.')
    deactivate_users.short_description = "❌ Deactivate selected users"

# ============================================
# VENDOR ADMIN (Enhanced Verification System)
# ============================================

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = [
        'company_name', 
        'get_email', 
        'verification_status_badge', 
        'trust_score_bar', 
        'rating_display',
        'workload_display', 
        'license_preview',
        'created_at'
    ]
    
    list_filter = [
        VendorStatusFilter, 
        TrustScoreFilter,
        'is_active', 
        'rating',
        'specializations',
        'created_at'
    ]
    
    search_fields = [
        'company_name', 
        'license_number', 
        'user__email', 
        'user__phone', 
        'gst_number',
        'user__first_name',
        'user__last_name'
    ]
    
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'workload_percentage',
        'trust_score_display',
        'license_document_preview',
        'ocr_data_formatted',
        'user_details'
    ]
    
    raw_id_fields = ['user']
    date_hierarchy = 'created_at'
    
    # Organized fieldsets for verification workflow
    fieldsets = (
        ('🔍 Verification Status', {
            'fields': (
                'verification_status',
                'license_verified',
                'trust_score',
                'trust_score_display'
            ),
            'description': 'Current verification state of this vendor'
        }),
        
        ('📋 Company Information', {
            'fields': ('user', 'user_details', 'company_name', 'license_number', 'gst_number'),
        }),
        
        ('📄 License Document', {
            'fields': ('license_document', 'license_document_preview'),
            'description': 'View and verify the submitted license document'
        }),
        
        ('🤖 AI Verification Data', {
            'fields': ('ocr_data_formatted', 'forensics_score'),
            'classes': ('collapse',),
            'description': 'AI-extracted data from license document'
        }),
        
        ('⚙️ Business Configuration', {
            'fields': (
                'specializations', 
                'processing_capacity', 
                'current_workload', 
                'workload_percentage'
            ),
        }),
        
        ('📊 Performance Metrics', {
            'fields': (
                'rating', 
                'total_recycled', 
                'successful_evaluations', 
                'disputed_evaluations'
            ),
        }),
        
        ('🚨 Account Status', {
            'fields': (
                'is_active', 
                'suspension_count', 
                'last_suspension_date'
            ),
            'classes': ('collapse',),
        }),
        
        ('📝 Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    # Custom actions for bulk operations
    actions = [
        'approve_vendors', 
        'reject_vendors',
        'suspend_vendors', 
        'unsuspend_vendors',
        'mark_under_review',
        'reset_rating',
        'calculate_trust_scores'
    ]
    
    # Detailed display methods
    def get_email(self, obj):
        return obj.user.email if obj.user else '-'
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def user_details(self, obj):
        if not obj.user:
            return '-'
        return format_html(
            '<div style="background: #f7fafc; padding: 15px; border-radius: 8px;">'
            '<p><strong>Name:</strong> {} {}</p>'
            '<p><strong>Phone:</strong> {}</p>'
            '<p><strong>Address:</strong> {}, {}, {} - {}</p>'
            '<p><strong>Joined:</strong> {}</p>'
            '</div>',
            obj.user.first_name,
            obj.user.last_name,
            obj.user.phone,
            obj.user.address or '-',
            obj.user.city or '-',
            obj.user.state or '-',
            obj.user.pincode or '-',
            obj.user.date_joined.strftime('%Y-%m-%d')
        )
    user_details.short_description = 'User Profile Details'
    
    def verification_status_badge(self, obj):
        colors = {
            'pending': ('#ecc94b', '⏳'),      # yellow
            'under_review': ('#4299e1', '🔍'), # blue
            'approved': ('#48bb78', '✅'),      # green
            'rejected': ('#f56565', '❌'),      # red
            'suspended': ('#805ad5', '🚫')     # purple
        }
        color, icon = colors.get(obj.verification_status, ('gray', ''))
        return format_html(
            '<span style="background: {}; color: white; padding: 6px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600;">{} {}</span>',
            color, icon, obj.get_verification_status_display()
        )
    verification_status_badge.short_description = 'Status'
    verification_status_badge.admin_order_field = 'verification_status'
    
    def trust_score_bar(self, obj):
        score = obj.trust_score or 0
        if score >= 90:
            color = '#48bb78'  # green
            text_color = 'white'
        elif score >= 70:
            color = '#ecc94b'  # yellow
            text_color = 'black'
        elif score >= 50:
            color = '#ed8936'  # orange
            text_color = 'white'
        else:
            color = '#f56565'  # red
            text_color = 'white'
        
        return format_html(
            '<div style="position: relative; width: 150px; height: 25px; background: #e2e8f0; border-radius: 12px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background: {}; display: flex; align-items: center; justify-content: center; color: {}; font-weight: bold; font-size: 0.85em;">'
            '{:.0f}/100'
            '</div></div>',
            score, color, text_color, score
        )
    trust_score_bar.short_description = 'Trust Score'
    
    def trust_score_display(self, obj):
        return self.trust_score_bar(obj)
    trust_score_display.short_description = 'Trust Score Visualization'
    
    def rating_display(self, obj):
        stars = '⭐' * int(obj.rating) if obj.rating else '☆☆☆☆☆'
        return format_html('<span title="Rating: {}/5">{} {}</span>', obj.rating, stars, obj.rating)
    rating_display.short_description = 'Rating'
    
    def workload_display(self, obj):
        percentage = obj.workload_percentage
        if percentage >= 90:
            color = '#f56565'  # red
            status = '🚨 Full'
        elif percentage >= 70:
            color = '#ed8936'  # orange
            status = '⚠️ Busy'
        else:
            color = '#48bb78'  # green
            status = '✅ OK'
        
        return format_html(
            '<span style="color: {}; font-weight: 600;">{:.1f}% {}</span>',
            color, percentage, status
        )
    workload_display.short_description = 'Load'
    
    def license_preview(self, obj):
        if obj.license_document:
            file_url = obj.license_document.url
            file_name = obj.license_document.name.split('/')[-1]
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                return format_html(
                    '<a href="{}" target="_blank">'
                    '<img src="{}" style="max-height: 50px; border-radius: 4px; border: 1px solid #ddd;" title="Click to view full size"/>'
                    '</a>',
                    file_url, file_url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank" style="background: #4299e1; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 0.85em;">'
                    '📄 View PDF'
                    '</a>',
                    file_url
                )
        return format_html('<span style="color: #a0aec0;">No file</span>')
    license_preview.short_description = 'License'
    
    def license_document_preview(self, obj):
        if not obj.license_document:
            return format_html('<p style="color: #e53e3e;">❌ No license document uploaded</p>')
        
        file_url = obj.license_document.url
        file_name = obj.license_document.name.split('/')[-1]
        
        if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            return format_html(
                '<div style="border: 2px solid #e2e8f0; padding: 10px; border-radius: 8px; max-width: 500px;">'
                '<p><strong>📷 Image Preview:</strong></p>'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 100%; max-height: 400px; border-radius: 4px;"/>'
                '</a>'
                '<p style="margin-top: 10px;"><a href="{}" target="_blank" style="color: #4299e1;">🔍 Open in new tab</a></p>'
                '</div>',
                file_url, file_url, file_url
            )
        else:
            return format_html(
                '<div style="border: 2px solid #e2e8f0; padding: 20px; border-radius: 8px; text-align: center; background: #f7fafc;">'
                '<p style="font-size: 3em; margin: 0;">📄</p>'
                '<p><strong>PDF Document</strong></p>'
                '<p style="color: #718096; font-size: 0.9em;">{}</p>'
                '<a href="{}" target="_blank" style="display: inline-block; margin-top: 10px; background: #4299e1; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">'
                'Open PDF Document'
                '</a>'
                '</div>',
                file_name, file_url
            )
    license_document_preview.short_description = 'Document Preview'
    
    def ocr_data_formatted(self, obj):
        if not obj.ocr_data:
            return format_html('<p style="color: #a0aec0;">No OCR data available</p>')
        
        html = '<div style="background: #f7fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #4299e1;">'
        html += '<h4 style="margin-top: 0; color: #2d3748;">🤖 AI Extracted Data:</h4>'
        html += '<table style="width: 100%;">'
        
        for key, value in obj.ocr_data.items():
            html += '<tr>'
            html += '<td style="padding: 5px; color: #718096; font-weight: 600; width: 30%;">{}</td>'.format(key.replace('_', ' ').title())
            html += '<td style="padding: 5px; color: #2d3748;">{}</td>'.format(value)
            html += '</tr>'
        
        html += '</table>'
        html += '</div>'
        return mark_safe(html)
    ocr_data_formatted.short_description = 'OCR Analysis Results'
    
    # ==========================================
    # CUSTOM ACTIONS
    # ==========================================
    
    def approve_vendors(self, request, queryset):
        """Approve selected vendors and activate their accounts"""
        approved_count = 0
        for vendor in queryset:
            if vendor.verification_status != 'approved':
                vendor.verification_status = 'approved'
                vendor.is_active = True
                vendor.license_verified = True
                vendor.save()
                approved_count += 1
        
        messages.success(request, f'✅ Approved {approved_count} vendor(s). They can now start operations.')
    approve_vendors.short_description = "✅ Approve selected vendors"
    
    def reject_vendors(self, request, queryset):
        """Reject vendors with notification"""
        queryset.update(verification_status='rejected', is_active=False)
        messages.warning(request, f'❌ Rejected {queryset.count()} vendor(s). Access denied.')
    reject_vendors.short_description = "❌ Reject selected vendors"
    
    def mark_under_review(self, request, queryset):
        """Mark vendors as under review"""
        queryset.update(verification_status='under_review')
        messages.info(request, f'🔍 Marked {queryset.count()} vendor(s) as under review.')
    mark_under_review.short_description = "🔍 Mark as Under Review"
    
    def suspend_vendors(self, request, queryset):
        """Suspend vendor operations"""
        queryset.update(
            verification_status='suspended', 
            is_active=False,
            last_suspension_date=timezone.now()
        )
        messages.error(request, f'🚫 Suspended {queryset.count()} vendor(s).')
    suspend_vendors.short_description = "🚫 Suspend vendors"
    
    def unsuspend_vendors(self, request, queryset):
        """Reactivate suspended vendors"""
        queryset.update(verification_status='approved', is_active=True)
        messages.success(request, f'✅ Unsuspended {queryset.count()} vendor(s).')
    unsuspend_vendors.short_description = "✅ Unsuspend vendors"
    
    def reset_rating(self, request, queryset):
        queryset.update(rating=5.0, successful_evaluations=0, disputed_evaluations=0)
        messages.info(request, f'🔄 Reset rating for {queryset.count()} vendor(s).')
    reset_rating.short_description = "🔄 Reset rating to 5.0"
    
    def calculate_trust_scores(self, request, queryset):
        """Recalculate trust scores based on current metrics"""
        updated = 0
        for vendor in queryset:
            # Simple algorithm: Base 50 + forensics (30) + rating (20)
            forensics = vendor.forensics_score or 0
            rating_score = (vendor.rating / 5) * 20
            new_score = min(100, 50 + (forensics * 0.3) + rating_score)
            vendor.trust_score = new_score
            vendor.save()
            updated += 1
        
        messages.success(request, f'🤖 Recalculated trust scores for {updated} vendor(s).')
    calculate_trust_scores.short_description = "🤖 Recalculate Trust Scores"
    
    # ==========================================
    # CUSTOM ADMIN VIEWS (URLs)
    # ==========================================
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/verify/',
                self.admin_site.admin_view(self.verify_vendor_view),
                name='verify_vendor_detail',
            ),
        ]
        return custom_urls + urls
    
    def verify_vendor_view(self, request, object_id):
        """Custom detailed verification view"""
        vendor = get_object_or_404(Vendor, pk=object_id)
        
        if request.method == 'POST':
            action = request.POST.get('action')
            notes = request.POST.get('admin_notes', '')
            
            if action == 'approve':
                vendor.verification_status = 'approved'
                vendor.is_active = True
                vendor.license_verified = True
                vendor.save()
                messages.success(request, f'✅ Approved {vendor.company_name}')
                
            elif action == 'reject':
                vendor.verification_status = 'rejected'
                vendor.is_active = False
                vendor.save()
                messages.error(request, f'❌ Rejected {vendor.company_name}')
                
            elif action == 'review':
                vendor.verification_status = 'under_review'
                vendor.save()
                messages.info(request, f'🔍 Marked {vendor.company_name} for review')
            
            return redirect('admin:core_vendor_change', object_id)
        
        context = {
            **self.admin_site.each_context(request),
            'vendor': vendor,
            'title': f'Verify Vendor: {vendor.company_name}',
            'opts': self.model._meta,
        }
        return render(request, 'admin/core/vendor/verify_detail.html', context)


# ============================================
# COLLECTOR ADMIN (Full Verification System)
# ============================================

class CollectorStatusFilter(admin.SimpleListFilter):
    title = _('verification status')
    parameter_name = 'verification_status'
    
    def lookups(self, request, model_admin):
        return (
            ('pending', _('⏳ Pending')),
            ('documents_pending', _('📄 Docs Missing')),
            ('under_review', _('🔍 Under Review')),
            ('approved', _('✅ Approved')),
            ('rejected', _('❌ Rejected')),
            ('suspended', _('🚫 Suspended')),
        )
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(verification_status=self.value())
        return queryset

@admin.register(Collector)
class CollectorAdmin(admin.ModelAdmin):
    list_display = [
        'get_name',
        'get_email', 
        'vehicle_display',
        'verification_badge',
        'document_status',
        'availability_badge',
        'current_pickups',
        'rating',
        'created_at'
    ]
    
    list_filter = [
        CollectorStatusFilter,
        'vehicle_type',
        'is_available',
        'rating',
        'created_at'
    ]
    
    search_fields = [
        'user__email',
        'user__phone',
        'user__first_name',
        'user__last_name',
        'vehicle_number',
        'driving_license_number'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'verified_by',
        'verified_at',
        'profile_photo_preview',
        'license_front_preview',
        'license_back_preview',
        'vehicle_doc_preview',
        'user_info',
        'is_documentation_complete'
    ]
    
    raw_id_fields = ['user', 'permanent_vendor']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('🔍 Verification Status', {
            'fields': (
                'verification_status',
                'is_verified',
                'verified_by',
                'verified_at'
            ),
            'description': 'Verification workflow status'
        }),
        
        ('👤 User Information', {
            'fields': ('user', 'user_info'),
        }),
        
        ('📸 Identity & Documents', {
            'fields': (
                'profile_photo',
                'profile_photo_preview',
                'driving_license_front',
                'license_front_preview',
                'driving_license_back',
                'license_back_preview',
                'vehicle_registration',
                'vehicle_doc_preview',
                'police_verification_doc',
                'is_documentation_complete'
            ),
            'description': 'Required documents for verification'
        }),
        
        ('🚗 Vehicle Details', {
            'fields': (
                'vehicle_type',
                'vehicle_number',
                'driving_license_number',
                'license_expiry_date'
            ),
        }),
        
        ('📊 Work Status', {
            'fields': (
                'is_available',
                'current_pickups',
                'total_deliveries',
                'rating',
                'permanent_vendor',
                'service_area'
            ),
        }),
        
        ('🚨 Safety & Incidents', {
            'fields': (
                'incident_count',
                'customer_complaints',
                'last_incident_date',
                'is_blacklisted',
                'blacklist_reason',
                'emergency_contact_name',
                'emergency_contact_phone'
            ),
            'classes': ('collapse',),
        }),
        
        ('📝 Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = [
        'approve_collectors',
        'reject_collectors',
        'mark_docs_pending',
        'suspend_collectors',
        'unsuspend_collectors',
        'blacklist_collectors',
        'reset_rating'
    ]
    
    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def user_info(self, obj):
        if not obj.user:
            return '-'
        return format_html(
            '<div style="background: #f7fafc; padding: 15px; border-radius: 8px;">'
            '<p><strong>Phone:</strong> {}</p>'
            '<p><strong>Joined:</strong> {}</p>'
            '<p><strong>Wallet:</strong> ₹{}</p>'
            '</div>',
            obj.user.phone,
            obj.user.date_joined.strftime('%Y-%m-%d'),
            obj.user.wallet_balance
        )
    user_info.short_description = 'User Details'
    
    def verification_badge(self, obj):
        colors = {
            'pending': ('#ecc94b', '⏳'),
            'documents_pending': ('#ed8936', '📄'),
            'under_review': ('#4299e1', '🔍'),
            'approved': ('#48bb78', '✅'),
            'rejected': ('#f56565', '❌'),
            'suspended': ('#805ad5', '🚫'),
            'blacklisted': ('#1a202c', '⛔')
        }
        color, icon = colors.get(obj.verification_status, ('gray', ''))
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 10px; border-radius: 12px; font-weight: 600;">{} {}</span>',
            color, icon, obj.get_verification_status_display()
        )
    verification_badge.short_description = 'Status'
    
    def document_status(self, obj):
        if obj.is_documentation_complete:
            return format_html('<span style="color: #48bb78; font-weight: bold;">✅ Complete</span>')
        missing = []
        if not obj.profile_photo:
            missing.append('Photo')
        if not obj.driving_license_front:
            missing.append('DL Front')
        if not obj.driving_license_back:
            missing.append('DL Back')
        return format_html(
            '<span style="color: #ed8936; font-weight: bold;">⚠️ Missing: {}</span>',
            ', '.join(missing)
        )
    document_status.short_description = 'Docs'
    
    def availability_badge(self, obj):
        if not obj.is_verified:
            return format_html('<span style="background: #a0aec0; color: white; padding: 4px 8px; border-radius: 10px;">🔒 Unverified</span>')
        if obj.is_blacklisted:
            return format_html('<span style="background: #1a202c; color: white; padding: 4px 8px; border-radius: 10px;">⛔ Blacklisted</span>')
        if obj.is_available and obj.current_pickups < 3:
            return format_html('<span style="background: #48bb78; color: white; padding: 4px 8px; border-radius: 10px;">🟢 Ready</span>')
        elif obj.is_available:
            return format_html('<span style="background: #ed8936; color: white; padding: 4px 8px; border-radius: 10px;">🟠 Full</span>')
        return format_html('<span style="background: #f56565; color: white; padding: 4px 8px; border-radius: 10px;">🔴 Offline</span>')
    availability_badge.short_description = 'Available'
    
    # Document preview methods
    def _get_image_preview(self, field_obj, label):
        if not field_obj:
            return format_html('<span style="color: #a0aec0;">No {} uploaded</span>', label)
        try:
            url = field_obj.url
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 8px; border: 2px solid #e2e8f0;"/></a>',
                url, url
            )
        except:
            return format_html('<span style="color: #e53e3e;">Error loading {}</span>', label)
    
    def profile_photo_preview(self, obj):
        return self._get_image_preview(obj.profile_photo, "profile photo")
    profile_photo_preview.short_description = 'Photo Preview'
    
    def license_front_preview(self, obj):
        return self._get_image_preview(obj.driving_license_front, "DL front")
    license_front_preview.short_description = 'DL Front Preview'
    
    def license_back_preview(self, obj):
        return self._get_image_preview(obj.driving_license_back, "DL back")
    license_back_preview.short_description = 'DL Back Preview'
    
    def vehicle_doc_preview(self, obj):
        if not obj.vehicle_registration:
            return format_html('<span style="color: #a0aec0;">Optional: Not uploaded</span>')
        return self._get_image_preview(obj.vehicle_registration, "vehicle RC")
    vehicle_doc_preview.short_description = 'Vehicle RC'
    
    # Actions
    def approve_collectors(self, request, queryset):
        from django.utils import timezone
        approved = 0
        for collector in queryset:
            if collector.is_documentation_complete:
                collector.verification_status = 'approved'
                collector.is_verified = True
                collector.is_available = True
                collector.verified_by = request.user
                collector.verified_at = timezone.now()
                collector.save()
                approved += 1
            else:
                collector.verification_status = 'documents_pending'
                collector.save()
        
        messages.success(request, f'✅ Approved {approved} collector(s). {queryset.count() - approved} missing documents.')
    approve_collectors.short_description = "✅ Approve (if docs complete)"
    
    def reject_collectors(self, request, queryset):
        queryset.update(verification_status='rejected', is_verified=False, is_available=False)
        messages.error(request, f'❌ Rejected {queryset.count()} collector(s).')
    reject_collectors.short_description = "❌ Reject"
    
    def mark_docs_pending(self, request, queryset):
        queryset.update(verification_status='documents_pending')
        messages.warning(request, f'📄 Marked {queryset.count()} as documents pending.')
    mark_docs_pending.short_description = "📄 Mark: Docs Required"
    
    def suspend_collectors(self, request, queryset):
        queryset.update(verification_status='suspended', is_available=False)
        messages.error(request, f'🚫 Suspended {queryset.count()} collector(s).')
    suspend_collectors.short_description = "🚫 Suspend"
    
    def unsuspend_collectors(self, request, queryset):
        queryset.update(verification_status='approved', is_available=True)
        messages.success(request, f'✅ Unsuspended {queryset.count()} collector(s).')
    unsuspend_collectors.short_description = "✅ Unsuspend"
    
    def blacklist_collectors(self, request, queryset):
        queryset.update(is_blacklisted=True, verification_status='blacklisted', is_available=False)
        messages.error(request, f'⛔ Blacklisted {queryset.count()} collector(s). REVERSIBLE!')
    blacklist_collectors.short_description = "⛔ BLacklist (Serious)"
    
    def reset_rating(self, request, queryset):
        queryset.update(rating=5.0, total_deliveries=0)
        messages.info(request, f'🔄 Reset rating for {queryset.count()} collector(s).')
    reset_rating.short_description = "🔄 Reset Stats"



# ============================================
# PRODUCT ADMIN
# ============================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id_short', 'category', 'get_customer', 'status_badge', 'assigned_vendor', 'uploaded_at']
    list_filter = ['status', 'category', 'uploaded_at']
    search_fields = ['customer__email', 'category', 'id']
    readonly_fields = ['uploaded_at', 'picked_up_at', 'delivered_at', 'completed_at']
    raw_id_fields = ['customer', 'assigned_vendor', 'assigned_collector']
    date_hierarchy = 'uploaded_at'
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def get_customer(self, obj):
        return obj.customer.email if obj.customer else '-'
    get_customer.short_description = 'Customer'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#718096',
            'classified': '#4299e1',
            'vendor_assigned': '#ed8936',
            'collector_assigned': '#805ad5',
            'picked_up': '#667eea',
            'delivered': '#38b2ac',
            'recycled': '#48bb78',
            'disputed': '#f56565'
        }
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.85em;">{}</span>', 
                          color, obj.get_status_display())
    status_badge.short_description = 'Status'

# ============================================
# FRAUD FLAG ADMIN
# ============================================

@admin.register(FraudFlag)
class FraudFlagAdmin(admin.ModelAdmin):
    list_display = ['product_id_short', 'get_vendor', 'risk_score_bar', 'admin_decision', 'created_at']
    list_filter = ['admin_reviewed', 'admin_decision', 'created_at']
    readonly_fields = ['created_at']
    
    def product_id_short(self, obj):
        return str(obj.product.id)[:8] if obj.product else '-'
    product_id_short.short_description = 'Product'
    
    def get_vendor(self, obj):
        if obj.product and obj.product.assigned_vendor:
            return obj.product.assigned_vendor.company_name
        return '-'
    get_vendor.short_description = 'Vendor'
    
    def risk_score_bar(self, obj):
        score = obj.risk_score or 0
        color = '#f56565' if score > 70 else '#ed8936' if score > 40 else '#ecc94b'
        return format_html('<div style="width: 100px; background: #eee; border-radius: 10px;"><div style="width: {}%; background: {}; height: 20px; border-radius: 10px; text-align: center; color: white; line-height: 20px;">{:.0f}</div></div>', 
                          min(score, 100), color, score)
    risk_score_bar.short_description = 'Risk'

# ============================================
# ADMIN SITE CONFIGURATION
# ============================================
admin.site.site_header = '🏭 E-RECYCLO Administration'
admin.site.site_title = 'E-RECYCLO Admin'
admin.site.index_title = 'Welcome to E-RECYCLO Management'