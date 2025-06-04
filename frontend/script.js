// Mock data based on the provided example
const mockData = {
    input: {
        transaction_data: {
            transaction_id: "TXN_001",
            transaction_description: "ủng hộ quỹ từ thiện mua xe điện cho bệnh viện",
            payment_method: "mobile banking",
            amount: 1000000,
            aml_flag: "clean"
        },
        sender_info: {
            sender_name: "Nguyen Van A",
            kyc_status: "verified"
        },
        receiver_info: {
            receiver_name: "Bệnh viện Nhi Trung Ương",
            business_type: "healthcare charity",
            kyc_status: "verified",
            environmental_certificates: ["ISO 14001"],
            business_license: "123456789",
            tax_code: "987654321",
            company_size: "large"
        }
    },
    response: {
        environment_score: 2.7,
        social_score: 3.0,
        governance_score: 1.3,
        total_esg_score: 7.0,
        analysis_results: {
            environment: {
                certificates: 1.0,
                keywords: 1.0,
                digital_payment: 0.7,
                total: 2.7,
                explaination_message_e: "Chứng chỉ ISO 14001 đạt 1.0 điểm; từ khóa 'xe điện' trong mô tả giao dịch đạt 1.0 điểm; phương thức thanh toán qua mobile banking đạt 0.7 điểm."
            },
            social: {
                organization_type: 2.0,
                purpose: 1.0,
                total: 3.0,
                explaination_message_s: "Tổ chức phi lợi nhuận (từ thiện), mục đích ủng hộ quỹ từ thiện."
            },
            governance: {
                kyc_reliability: 0.3,
                legal_compliance: 1.0,
                total: 1.3,
                explanation_message_g: "KYC của sender và receiver chỉ có thông tin cơ bản, điểm G1 là 0.3; tổ chức nhận có giấy phép kinh doanh rõ ràng, điểm G2 là 1.0."
            },
            breakdown: {
                total: 7.0
            },
            classification: "✅ Tốt"
        },
        report: "Giao dịch này thể hiện trách nhiệm xã hội rõ ràng qua việc ủng hộ quỹ từ thiện mua xe điện cho bệnh viện, góp phần nâng cao hình ảnh cộng đồng và môi trường. Tuy nhiên, điểm Governance còn thấp, phản ánh cần cải thiện về quản trị và minh bạch trong quá trình thực hiện. Điểm tổng thể 7.0/10 cho thấy mức độ phù hợp tốt, đặc biệt trong lĩnh vực môi trường và xã hội, nhưng vẫn còn nhiều tiềm năng để nâng cao quản trị doanh nghiệp.",
        advises: [
            "Tăng cường minh bạch và công khai các quy trình quản lý quỹ từ thiện để nâng cao điểm Governance.",
            "Xây dựng các chính sách rõ ràng về trách nhiệm xã hội và quản trị doanh nghiệp để thể hiện cam kết lâu dài.",
            "Thúc đẩy việc áp dụng các tiêu chuẩn quản trị quốc tế như ISO 37001 về chống tham nhũng để nâng cao uy tín.",
            "Tăng cường đào tạo và nâng cao nhận thức về quản trị doanh nghiệp cho các bên liên quan để cải thiện điểm Governance."
        ],
        errors: []
    }
};

// Chart instances
let radarChart = null;
let barChart = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    checkBackendConnection();
});

function initializeEventListeners() {
    // Load mock data button
    document.getElementById('load-mock-data').addEventListener('click', loadMockData);
    
    // Form submission
    document.getElementById('esg-form').addEventListener('submit', handleFormSubmit);
}

function loadMockData() {
    const data = mockData.input;
    
    // Transaction data
    document.getElementById('transaction_id').value = data.transaction_data.transaction_id;
    document.getElementById('description').value = data.transaction_data.transaction_description;
    document.getElementById('payment_method').value = data.transaction_data.payment_method;
    document.getElementById('amount').value = data.transaction_data.amount;
    document.getElementById('aml_flag').value = data.transaction_data.aml_flag;
    
    // Sender info
    document.getElementById('sender_name').value = data.sender_info.sender_name;
    document.getElementById('sender_kyc').value = data.sender_info.kyc_status;
    
    // Receiver info
    document.getElementById('receiver_name').value = data.receiver_info.receiver_name;
    document.getElementById('business_type').value = data.receiver_info.business_type;
    document.getElementById('receiver_kyc').value = data.receiver_info.kyc_status;
    document.getElementById('receiver_env_certificates').value = data.receiver_info.environmental_certificates?.join(', ') || '';
    document.getElementById('company_size').value = data.receiver_info.company_size;
    document.getElementById('business_license').value = data.receiver_info.business_license;
    document.getElementById('tax_code').value = data.receiver_info.tax_code;
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    // Show loading state
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    submitButton.disabled = true;
    
    // Get environmental certificates properly
    const envCertificatesInput = document.getElementById('receiver_env_certificates');
    const envCertificates = envCertificatesInput ? 
        envCertificatesInput.value.split(',').map(s => s.trim()).filter(s => s) : 
        [];
    
    const formData = {
        transaction_data: {
            transaction_id: document.getElementById('transaction_id').value,
            transaction_description: document.getElementById('description').value,
            payment_method: document.getElementById('payment_method').value,
            amount: parseFloat(document.getElementById('amount').value) || 0,
            aml_flag: document.getElementById('aml_flag').value
        },
        sender_info: {
            sender_name: document.getElementById('sender_name').value,
            kyc_status: document.getElementById('sender_kyc').value
        },
        receiver_info: {
            receiver_name: document.getElementById('receiver_name').value,
            business_type: document.getElementById('business_type').value,
            kyc_status: document.getElementById('receiver_kyc').value,
            environmental_certificates: envCertificates,
            business_license: document.getElementById('business_license').value,
            tax_code: document.getElementById('tax_code').value,
            company_size: document.getElementById('company_size').value
        }
    };

    try {
        console.log('Sending data to backend:', formData);
        
        // First, test if the backend is reachable
        console.log('Testing backend connection...');
        
        const response = await fetch('http://localhost:5000/api/esg', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        console.log('Response status:', response.status);
        console.log('Response headers:', [...response.headers.entries()]);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const responseData = await response.json();
        console.log('Received response:', responseData);

        if (responseData.success) {
            displayResults(responseData.data);
            document.getElementById('results').style.display = 'block';
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        } else {
            throw new Error(responseData.error || 'API returned unsuccessful response');
        }
    } catch (error) {
        console.error("Full error details:", error);
        
        let errorMsg = 'Unknown error occurred';
        let suggestions = [];
        
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            errorMsg = 'Cannot connect to backend server';
            suggestions = [
                'Make sure the backend server is running on port 5000',
                'Check if you ran: python application.py in the backend directory',
                'Verify the backend URL is correct (http://localhost:5000)',
                'Check for CORS issues or firewall blocking the connection'
            ];
        } else if (error.message.includes('HTTP')) {
            errorMsg = `Server error: ${error.message}`;
            suggestions = [
                'Check backend server logs for detailed error information',
                'Verify the API endpoint /api/esg exists and is working',
                'Check if all required dependencies are installed'
            ];
        } else {
            errorMsg = `Network error: ${error.message}`;
            suggestions = ['Check your internet connection', 'Try refreshing the page'];
        }
        
        // Show detailed error message
        const detailedError = `
${errorMsg}

Troubleshooting steps:
${suggestions.map(s => `• ${s}`).join('\n')}

Technical details: ${error.message}
        `.trim();
        
        alert(detailedError);
        
        // Fall back to mock data for demonstration
        console.log('Falling back to mock data for demonstration...');
        displayResults(mockData.response);
        document.getElementById('results').style.display = 'block';
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        
        // Show a notice about using mock data
        const mockNotice = document.createElement('div');
        mockNotice.className = 'alert alert-warning';
        mockNotice.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Notice:</strong> Backend connection failed. Showing mock data for demonstration.
            <br><small>Please start the backend server to use real analysis.</small>
        `;
        document.getElementById('results').insertBefore(mockNotice, document.getElementById('results').firstChild);
    } finally {
        // Reset button state
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    }
}

function displayResults(apiData) {
    // Use fallback to mock data if API data is incomplete
    const results = apiData.analysis_results || mockData.response.analysis_results;
    const environment = results.environment || {};
    const social = results.social || {};
    const governance = results.governance || {};
    const breakdown = results.breakdown || {};

    // Update score displays with proper fallbacks
    const totalScore = breakdown.total !== undefined ? breakdown.total : mockData.response.total_esg_score;
    const envScore = environment.total !== undefined ? environment.total : mockData.response.environment_score;
    const socialScore = social.total !== undefined ? social.total : mockData.response.social_score;
    const govScore = governance.total !== undefined ? governance.total : mockData.response.governance_score;

    document.getElementById('total-score').textContent = totalScore.toFixed(1);
    document.getElementById('env-score').textContent = envScore.toFixed(1);
    document.getElementById('social-score').textContent = socialScore.toFixed(1);
    document.getElementById('gov-score').textContent = govScore.toFixed(1);
    document.getElementById('classification').textContent = results.classification || mockData.response.analysis_results.classification;
    
    // Update detailed analysis with proper fallbacks
    document.getElementById('env-details').innerHTML = `
        <p><strong>Certificates:</strong> ${environment.certificates !== undefined ? environment.certificates.toFixed(1) : 'N/A'}/1.0</p>
        <p><strong>Keywords:</strong> ${environment.keywords !== undefined ? environment.keywords.toFixed(1) : 'N/A'}/1.0</p>
        <p><strong>Digital Payment:</strong> ${environment.digital_payment !== undefined ? environment.digital_payment.toFixed(1) : 'N/A'}/1.0</p>
        <p class="explanation">${environment.explaination_message_e || environment.explanation_message_e || 'No environmental explanation available.'}</p>
    `;
    
    document.getElementById('social-details').innerHTML = `
        <p><strong>Organization Type:</strong> ${social.organization_type !== undefined ? social.organization_type.toFixed(1) : 'N/A'}/2.0</p>
        <p><strong>Purpose:</strong> ${social.purpose !== undefined ? social.purpose.toFixed(1) : 'N/A'}/1.0</p>
        <p class="explanation">${social.explaination_message_s || social.explanation_message_s || 'No social explanation available.'}</p>
    `;
    
    document.getElementById('gov-details').innerHTML = `
        <p><strong>KYC Reliability:</strong> ${governance.kyc_reliability !== undefined ? governance.kyc_reliability.toFixed(1) : 'N/A'}/1.0</p>
        <p><strong>Legal Compliance:</strong> ${governance.legal_compliance !== undefined ? governance.legal_compliance.toFixed(1) : 'N/A'}/1.0</p>
        <p class="explanation">${governance.explanation_message_g || governance.explanation_message_g || 'No governance explanation available.'}</p>
    `;
    
    // Update report and recommendations
    document.getElementById('report-text').textContent = apiData.general_evaluation || mockData.response.report;
    
    const recommendationsList = document.getElementById('recommendations-list');
    recommendationsList.innerHTML = '';
    const advises = apiData.advises || mockData.response.advises;
    if (advises && advises.length > 0) {
        advises.forEach(advice => {
            const li = document.createElement('li');
            li.textContent = advice;
            recommendationsList.appendChild(li);
        });
    } else {
        recommendationsList.innerHTML = '<li>No specific recommendations available.</li>';
    }
    
    // Create charts
    createRadarChart(apiData); 
    createBarChart(apiData);
}

function createRadarChart(apiData) { // apiData is responseData.data from backend
    const ctx = document.getElementById('esg-radar-chart').getContext('2d');
    const results = apiData.analysis_results || {};
    const environmentScore = (results.environment && results.environment.total !== undefined) ? results.environment.total : mockData.response.environment_score;
    const socialScore = (results.social && results.social.total !== undefined) ? results.social.total : mockData.response.social_score;
    const governanceScore = (results.governance && results.governance.total !== undefined) ? results.governance.total : mockData.response.governance_score;

    if (radarChart) {
        radarChart.destroy();
    }
    
    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Environment', 'Social', 'Governance'],
            datasets: [{
                label: 'ESG Scores',
                data: [environmentScore, socialScore, governanceScore],
                borderColor: 'rgba(55, 65, 81, 1)', // Darker gray
                backgroundColor: 'rgba(107, 114, 128, 0.2)', // Lighter gray, transparent
                borderWidth: 2,
                pointBackgroundColor: 'rgba(55, 65, 81, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'ESG Score Radar Chart',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 5,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    pointLabels: {
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
}

function createBarChart(apiData) { // apiData is responseData.data from backend
    const ctx = document.getElementById('esg-bar-chart').getContext('2d');
    const results = apiData.analysis_results || {};
    const environmentScore = (results.environment && results.environment.total !== undefined) ? results.environment.total : mockData.response.environment_score;
    const socialScore = (results.social && results.social.total !== undefined) ? results.social.total : mockData.response.social_score;
    const governanceScore = (results.governance && results.governance.total !== undefined) ? results.governance.total : mockData.response.governance_score;
    
    if (barChart) {
        barChart.destroy();
    }
    
    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Environment', 'Social', 'Governance'],
            datasets: [{
                label: 'ESG Scores',
                data: [environmentScore, socialScore, governanceScore],
                backgroundColor: [
                    'rgba(107, 114, 128, 0.7)', // Medium Gray for Environment
                    'rgba(75, 85, 99, 0.7)',    // Darker Gray for Social
                    'rgba(156, 163, 175, 0.7)'  // Lighter Gray for Governance
                ],
                borderColor: [
                    'rgba(55, 65, 81, 1)',
                    'rgba(31, 41, 55, 1)',
                    'rgba(107, 114, 128, 1)'
                ],
                borderWidth: 2,
                borderRadius: 4, // Adjusted from 8 to 4 for a more subtle look
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'ESG Score Breakdown',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: '#1f2937' // Dark gray for title
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    grid: {
                        color: 'rgba(107, 114, 128, 0.2)'
                    },
                    ticks: {
                        font: {
                            size: 12
                        },
                        color: '#6B7280'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12,
                            weight: 'bold'
                        },
                        color: '#374151'
                    }
                }
            }
        }
    });
}

// Check backend connectivity
async function checkBackendConnection() {
    const statusElement = document.getElementById('connection-status');
    const noticeElement = document.getElementById('backend-notice');
    const statusText = document.getElementById('backend-status-text');
    
    try {
        // Use the correct test endpoint
        const response = await fetch('http://localhost:5000/api/test', {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Backend connection successful:', data);
            statusElement.innerHTML = '<i class="fas fa-circle" style="color: green;"></i> <span>Backend connected</span>';
            statusText.textContent = 'Connected and ready';
            noticeElement.className = 'backend-notice success';
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Backend connection failed:', error);
        statusElement.innerHTML = '<i class="fas fa-circle" style="color: red;"></i> <span>Backend disconnected</span>';
        statusText.textContent = 'Not connected - using mock data for demo';
        noticeElement.className = 'backend-notice warning';
    }
    
    noticeElement.style.display = 'block';
}

// Additional utility functions for future enhancements
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

function getScoreColor(score, maxScore = 5) {
    const percentage = score / maxScore;
    if (percentage >= 0.8) return '#38a169'; // Green
    if (percentage >= 0.6) return '#3182ce'; // Blue
    if (percentage >= 0.4) return '#d69e2e'; // Yellow
    return '#e53e3e'; // Red
}

function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = progress * (end - start) + start;
        element.textContent = value.toFixed(1);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}