# Errors: run_001

| # | subject | gold queue / prio | predicted queue / prio | why |
|---|---|---|---|---|
| 0 | Irregular Data Analytics Outputs on Investment Optimization Tool | Product Support / low | Technical Support / medium | queue-overlap: tool malfunction, model picked Technical over Product; prio +1 |
| 1 | Enhance Data Analytics Investments | Customer Service / medium | Product Support / medium | definition-mismatch: optimisation advice is Customer Service in gold, model guessed Product |
| 2 | Concerns Regarding Subscription Billing Services | Billing and Payments / high | Billing and Payments / medium | prio-off-by-one: 6-word body, no urgency cue, gold says high |
| 3 | Request for Information on HIPAA Compliance for NAS-System | Customer Service / high | Product Support / low | definition-mismatch: compliance info request; model under-rated HIPAA urgency (low vs high) |
| 4 |  | Customer Service / low | Product Support / medium | definition-mismatch: docs request is Customer Service in gold; prio +1 |
| 5 | Problem with Data Feed During Nighttime | Technical Support / medium | Technical Support / high | prio-off-by-one: 'ceased to function' read as high |
| 6 | Inquiry About Data Security Measures for Hospital Systems | Sales and Pre-Sales / low | Sales and Pre-Sales / medium | prio-off-by-one: queue right; docs request over-rated |
| 7 | Technical Support Compatibility Problems | Product Support / high | Technical Support / high | queue-overlap: product compatibility crash, Technical vs Product |
| 8 | Digital Assistance Needed | IT Support / low | Service Outages and Maintenance / high | outage-keyword: 'outages' pulled it to Service Outages; gold IT/low |
| 9 | Recurring Crashes in SaaS Project Management Platform | IT Support / high | Technical Support / high | queue-overlap: platform crashes, Technical vs IT |
| 11 | Inquiry on System Requirements for H2O.ai Integration | Technical Support / high | Sales and Pre-Sales / medium | definition-mismatch: pre-integration requirements looked like Sales; gold Technical/high |
| 12 | Strengthened Safeguards for Medical Information | Service Outages and Maintenance / high | IT Support / high | label-noise: security change request labelled Service Outages |
| 13 | Investments Optimization Tool Problem | Product Support / medium | Technical Support / high | queue-overlap: same pattern as #0, Technical vs Product; prio +1 |
| 14 | H2O.ai Investment Optimization Analytics Tools | Billing and Payments / medium | Sales and Pre-Sales / low | label-noise: tool compatibility question labelled Billing |
| 15 | Security Breach in Medical Data | Technical Support / high | IT Support / high | queue-overlap: security breach, IT vs Technical |
| 17 |  | Customer Service / low | Technical Support / high | label-noise: data-discrepancy incident labelled Customer Service/low |
| 18 | WooCommerce Analytics Integration Assistance | Customer Service / medium | Product Support / medium | definition-mismatch: setup guidance, Customer Service vs Product |
| 19 | Problem with Website Downtime | Technical Support / medium | Service Outages and Maintenance / high | outage-keyword: 'downtime' pulled it to Service Outages; gold Technical |
| 21 | Needed Guidance on Secure Medical Data | Product Support / low | Product Support / medium | prio-off-by-one: queue right; guidance request over-rated |
| 22 | Inquiry on Data Analytics Solutions for Investment Strategies Optimization | Product Support / medium | Sales and Pre-Sales / low | definition-mismatch: 'solutions available?' read as Sales; gold Product |
| 23 | Inquiry About Marketing Agency Information | Customer Service / low | Sales and Pre-Sales / low | definition-mismatch: services info read as Sales; gold Customer Service |
| 24 | Boosting Digital Campaign Tools | Technical Support / low | Sales and Pre-Sales / low | too-short: 5-word body, not enough signal |
| 25 | Need Technical Assistance | IT Support / medium | Technical Support / high | queue-overlap: halted systems, Technical vs IT; prio +1 |
| 26 | Concern About Marketing Campaign | Customer Service / high | Technical Support / medium | definition-mismatch: integration issue is Customer Service/high in gold |
| 27 | Acknowledgment of Data Breach Concern | Product Support / high | Technical Support / high | label-noise: body is an agent reply, not a customer ticket |
| 28 | Concern About Unauthorized Access | IT Support / high | Technical Support / high | queue-overlap: unauthorized access, Technical vs IT |
| 29 | Strategies for Promoting the Joystick Product | Billing and Payments / medium | Sales and Pre-Sales / low | label-noise: marketing advice labelled Billing |
| 30 | Improve Customer Support Strategies | Returns and Exchanges / low | Sales and Pre-Sales / low | label-noise: strategy request labelled Returns and Exchanges |
| 33 | Problem with Duplicate Charges on Lately Subscribed Services | Billing and Payments / medium | Billing and Payments / high | prio-off-by-one: duplicate charges read as high; gold medium |
| 34 | Urgent: Incident Involving Data Breach in Medical Records Security | Product Support / medium | IT Support / high | too-short: one-line breach report; model chose IT/high, gold Product/medium |
| 35 | Boost Brand Expansion Tactics | Customer Service / medium | Product Support / low | definition-mismatch: brand advice, Customer Service vs Product |
| 37 | Strategies for Safeguarding Hospital Patient Data | Technical Support / high | Product Support / medium | definition-mismatch: advice request is Technical/high in gold; model Product/medium |
| 38 | Trouble with Bose QuietComfort 35 II Gaming Headset Connectivity | IT Support / medium | Technical Support / medium | queue-overlap: headset connectivity, Technical vs IT |
| 39 | Problem with IBM SPSS Statistics | Technical Support / medium | Technical Support / high | prio-off-by-one: 'frustrating, impacts productivity' read as high |
| 40 | Issue with Decline in Digital Campaign Performance | Technical Support / medium | Product Support / medium | queue-overlap: campaign performance, Product vs Technical |
| 42 | Tools for Data Analytics with QuickBooks Online for Investment Optimization | IT Support / medium | Sales and Pre-Sales / low | label-noise: tool recommendation labelled IT Support |
| 43 |  | Customer Service / low | IT Support / high | label-noise: data breach labelled Customer Service/low |
| 46 | Enhance Project Management Efficiency Through Integration of Additional Tools | Customer Service / low | Product Support / low | definition-mismatch: integration request, Customer Service vs Product |
| 47 | Troubleshooting Data Integration Issues with Financial Analysis Tools and Scanners | Technical Support / high | Technical Support / medium | label-noise: body is an agent reply; prio -1 |
| 49 | Crash During Campaign Launch Today | Technical Support / high | Service Outages and Maintenance / high | outage-keyword: 'website crashed' pulled it to Service Outages; gold Technical |

## Tag counts

- definition-mismatch: 11
- queue-overlap: 9
- label-noise: 9
- prio-off-by-one: 6
- outage-keyword: 3
- too-short: 2
