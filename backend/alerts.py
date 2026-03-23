"""
Alert System Module for TRINETRA AI

This module implements the alert checking functionality that identifies
high-risk conditions in trade transactions based on predefined thresholds.
"""

from typing import List, Dict, Tuple, Optional
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json


from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import json

class AlertPriority(Enum):
    """
    Priority levels for fraud alerts.
    
    Priority is determined by:
    1. Risk category (FRAUD > SUSPICIOUS > SAFE)
    2. Number of alert triggers
    3. Severity of individual alert conditions
    """
    CRITICAL = 4  # FRAUD category with multiple alerts
    HIGH = 3      # FRAUD category or multiple severe alerts
    MEDIUM = 2    # SUSPICIOUS category or single severe alert
    LOW = 1       # SUSPICIOUS category with minor alerts


class AlertSeverity(Enum):
    """
    Severity levels for individual alert types.
    
    Severity is based on the typical impact and frequency of each alert type.
    """
    HIGH = 3      # High-risk company, significant price anomaly
    MEDIUM = 2    # Route anomaly, port congestion
    LOW = 1       # Minor alerts


# Alert type to severity mapping
ALERT_SEVERITY_MAP = {
    "PRICE_ANOMALY": AlertSeverity.HIGH,
    "HIGH_RISK_COMPANY": AlertSeverity.HIGH,
    "ROUTE_ANOMALY": AlertSeverity.MEDIUM,
    "PORT_CONGESTION": AlertSeverity.MEDIUM,
}


@dataclass
class Alert:
    """
    Data structure representing a single fraud alert.
    
    This class encapsulates all information about a triggered alert,
    including the transaction it relates to, the type of alert, severity,
    and when it was detected.
    
    Attributes:
        transaction_id (str): Unique identifier for the transaction
        alert_type (str): Type of alert (PRICE_ANOMALY, ROUTE_ANOMALY, etc.)
        severity (AlertSeverity): Severity level of the alert
        timestamp (datetime): When the alert was generated
        transaction_data (Optional[Dict]): Full transaction data for context
        message (Optional[str]): Human-readable alert message
        metadata (Dict): Additional alert-specific metadata
        dismissed (bool): Whether the alert has been dismissed by a user
        dismissed_at (Optional[datetime]): When the alert was dismissed
        dismissed_by (Optional[str]): User who dismissed the alert
    """
    transaction_id: str
    alert_type: str
    severity: AlertSeverity
    timestamp: datetime = field(default_factory=datetime.now)
    transaction_data: Optional[Dict] = None
    message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    dismissed: bool = False
    dismissed_at: Optional[datetime] = None
    dismissed_by: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """
        Convert alert to dictionary for JSON serialization.
        
        Returns:
            Dict: Alert data as dictionary with serializable values
        """
        data = asdict(self)
        # Convert enum to string
        data['severity'] = self.severity.name
        # Convert datetime to ISO format string
        data['timestamp'] = self.timestamp.isoformat()
        # Convert dismissed_at to ISO format string if present
        if self.dismissed_at:
            data['dismissed_at'] = self.dismissed_at.isoformat()
        return data
    
    def to_json(self) -> str:
        """
        Convert alert to JSON string.
        
        Returns:
            str: JSON representation of the alert
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Alert':
        """
        Create Alert instance from dictionary.
        
        Args:
            data (Dict): Alert data dictionary
        
        Returns:
            Alert: New Alert instance
        """
        # Convert severity string back to enum
        if isinstance(data.get('severity'), str):
            data['severity'] = AlertSeverity[data['severity']]
        
        # Convert timestamp string back to datetime
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Convert dismissed_at string back to datetime
        if isinstance(data.get('dismissed_at'), str):
            data['dismissed_at'] = datetime.fromisoformat(data['dismissed_at'])
        
        return cls(**data)


@dataclass
class AlertSummary:
    """
    Summary of alerts for a transaction.
    
    This class aggregates multiple alerts for a single transaction
    and provides priority information and overall risk assessment.
    
    Attributes:
        transaction_id (str): Unique identifier for the transaction
        alerts (List[Alert]): List of triggered alerts
        priority (AlertPriority): Overall priority level
        risk_category (str): Transaction risk category (SAFE, SUSPICIOUS, FRAUD)
        alert_count (int): Number of alerts triggered
        severity_score (int): Total severity score
        priority_reason (str): Explanation of priority assignment
        timestamp (datetime): When the summary was generated
        dismissed (bool): Whether all alerts have been dismissed
        dismissed_at (Optional[datetime]): When the alert summary was dismissed
        dismissed_by (Optional[str]): User who dismissed the alert summary
    """
    transaction_id: str
    alerts: List[Alert]
    priority: AlertPriority
    risk_category: str
    alert_count: int
    severity_score: int
    priority_reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    dismissed: bool = False
    dismissed_at: Optional[datetime] = None
    dismissed_by: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """
        Convert alert summary to dictionary for JSON serialization.
        
        Returns:
            Dict: Alert summary as dictionary with serializable values
        """
        return {
            'transaction_id': self.transaction_id,
            'alerts': [alert.to_dict() for alert in self.alerts],
            'priority': self.priority.name,
            'priority_value': self.priority.value,
            'risk_category': self.risk_category,
            'alert_count': self.alert_count,
            'severity_score': self.severity_score,
            'priority_reason': self.priority_reason,
            'timestamp': self.timestamp.isoformat(),
            'dismissed': self.dismissed,
            'dismissed_at': self.dismissed_at.isoformat() if self.dismissed_at else None,
            'dismissed_by': self.dismissed_by
        }
    
    def to_json(self) -> str:
        """
        Convert alert summary to JSON string.
        
        Returns:
            str: JSON representation of the alert summary
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AlertSummary':
        """
        Create AlertSummary instance from dictionary.
        
        Args:
            data (Dict): Alert summary data dictionary
        
        Returns:
            AlertSummary: New AlertSummary instance
        """
        # Convert alerts list
        if 'alerts' in data:
            data['alerts'] = [Alert.from_dict(a) if isinstance(a, dict) else a 
                            for a in data['alerts']]
        
        # Convert priority string back to enum
        if isinstance(data.get('priority'), str):
            data['priority'] = AlertPriority[data['priority']]
        
        # Convert timestamp string back to datetime
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Convert dismissed_at string back to datetime
        if isinstance(data.get('dismissed_at'), str):
            data['dismissed_at'] = datetime.fromisoformat(data['dismissed_at'])
        
        # Remove priority_value if present (it's derived from priority)
        data.pop('priority_value', None)
        
        return cls(**data)


def check_alerts(transaction: dict) -> List[str]:
    """
    Check a transaction for alert conditions and return triggered alerts.
    
    This function evaluates a transaction against four key risk thresholds:
    1. Price deviation exceeding 50%
    2. Route anomaly detected
    3. High company risk score
    4. Elevated port activity index
    
    Args:
        transaction (dict): Transaction data containing risk indicators
            Required keys:
            - price_deviation: float, percentage deviation from market price
            - route_anomaly: int, binary indicator (0 or 1)
            - company_risk_score: float, risk score for the company (0-1)
            - port_activity_index: float, port congestion indicator
    
    Returns:
        List[str]: List of alert strings for triggered conditions
            Possible alerts:
            - "PRICE_ANOMALY": price_deviation > 0.5
            - "ROUTE_ANOMALY": route_anomaly == 1
            - "HIGH_RISK_COMPANY": company_risk_score > 0.8
            - "PORT_CONGESTION": port_activity_index > 1.5
    
    Example:
        >>> transaction = {
        ...     'price_deviation': 0.6,
        ...     'route_anomaly': 1,
        ...     'company_risk_score': 0.85,
        ...     'port_activity_index': 1.2
        ... }
        >>> check_alerts(transaction)
        ['PRICE_ANOMALY', 'ROUTE_ANOMALY', 'HIGH_RISK_COMPANY']
    """
    alerts = []
    
    # Check price deviation threshold (> 50%)
    if transaction['price_deviation'] > 0.5:
        alerts.append("PRICE_ANOMALY")
    
    # Check route anomaly flag
    if transaction['route_anomaly'] == 1:
        alerts.append("ROUTE_ANOMALY")
    
    # Check company risk score threshold (> 80%)
    if transaction['company_risk_score'] > 0.8:
        alerts.append("HIGH_RISK_COMPANY")
    
    # Check port activity index threshold (> 1.5)
    if transaction['port_activity_index'] > 1.5:
        alerts.append("PORT_CONGESTION")
    
    return alerts


def create_alert_objects(transaction: dict, alert_types: List[str]) -> List[Alert]:
    """
    Create Alert objects from a transaction and list of alert types.
    
    This function converts simple alert type strings into rich Alert objects
    with full metadata, severity information, and human-readable messages.
    
    Args:
        transaction (dict): Transaction data
        alert_types (List[str]): List of alert type strings
    
    Returns:
        List[Alert]: List of Alert objects with full metadata
    
    Example:
        >>> transaction = {'transaction_id': 'TXN001', 'price_deviation': 0.6}
        >>> alert_types = ['PRICE_ANOMALY']
        >>> alerts = create_alert_objects(transaction, alert_types)
        >>> alerts[0].alert_type
        'PRICE_ANOMALY'
    """
    alerts = []
    transaction_id = transaction.get('transaction_id', 'UNKNOWN')
    
    # Alert message templates
    alert_messages = {
        'PRICE_ANOMALY': f"Price deviation of {transaction.get('price_deviation', 0):.1%} exceeds threshold",
        'ROUTE_ANOMALY': "Unusual shipping route detected",
        'HIGH_RISK_COMPANY': f"Company risk score of {transaction.get('company_risk_score', 0):.2f} exceeds threshold",
        'PORT_CONGESTION': f"Port activity index of {transaction.get('port_activity_index', 0):.2f} indicates congestion"
    }
    
    for alert_type in alert_types:
        severity = ALERT_SEVERITY_MAP.get(alert_type, AlertSeverity.LOW)
        message = alert_messages.get(alert_type, f"Alert triggered: {alert_type}")
        
        # Create metadata specific to alert type
        metadata = {}
        if alert_type == 'PRICE_ANOMALY':
            metadata = {
                'price_deviation': transaction.get('price_deviation'),
                'market_price': transaction.get('market_price'),
                'unit_price': transaction.get('unit_price')
            }
        elif alert_type == 'ROUTE_ANOMALY':
            metadata = {
                'shipping_route': transaction.get('shipping_route'),
                'route_anomaly': transaction.get('route_anomaly')
            }
        elif alert_type == 'HIGH_RISK_COMPANY':
            metadata = {
                'company_risk_score': transaction.get('company_risk_score'),
                'exporter_name': transaction.get('exporter_name'),
                'importer_name': transaction.get('importer_name')
            }
        elif alert_type == 'PORT_CONGESTION':
            metadata = {
                'port_activity_index': transaction.get('port_activity_index'),
                'export_port': transaction.get('export_port'),
                'import_port': transaction.get('import_port')
            }
        
        alert = Alert(
            transaction_id=transaction_id,
            alert_type=alert_type,
            severity=severity,
            transaction_data=transaction,
            message=message,
            metadata=metadata
        )
        alerts.append(alert)
    
    return alerts


def create_alert_summary(transaction: dict) -> Optional[AlertSummary]:
    """
    Create a complete AlertSummary for a transaction.
    
    This function checks alerts, creates Alert objects, calculates priority,
    and returns a comprehensive AlertSummary object.
    
    Args:
        transaction (dict): Transaction data
    
    Returns:
        Optional[AlertSummary]: AlertSummary object if alerts exist, None otherwise
    
    Example:
        >>> transaction = {
        ...     'transaction_id': 'TXN001',
        ...     'risk_category': 'FRAUD',
        ...     'price_deviation': 0.6,
        ...     'route_anomaly': 1,
        ...     'company_risk_score': 0.9,
        ...     'port_activity_index': 1.2
        ... }
        >>> summary = create_alert_summary(transaction)
        >>> summary.priority.name
        'CRITICAL'
    """
    # Check for alerts
    alert_types = check_alerts(transaction)
    
    if not alert_types:
        return None
    
    # Create Alert objects
    alerts = create_alert_objects(transaction, alert_types)
    
    # Calculate priority
    priority, metadata = prioritize_alert(transaction, alert_types)
    
    # Create summary
    summary = AlertSummary(
        transaction_id=transaction.get('transaction_id', 'UNKNOWN'),
        alerts=alerts,
        priority=priority,
        risk_category=transaction.get('risk_category', 'UNKNOWN'),
        alert_count=metadata['alert_count'],
        severity_score=metadata['severity_score'],
        priority_reason=metadata['priority_reason']
    )
    
    return summary



def calculate_alert_severity_score(alerts: List[str]) -> int:
    """
    Calculate the total severity score for a list of alerts.
    
    Args:
        alerts (List[str]): List of alert strings
    
    Returns:
        int: Total severity score (sum of individual alert severities)
    
    Example:
        >>> calculate_alert_severity_score(['PRICE_ANOMALY', 'ROUTE_ANOMALY'])
        5  # HIGH (3) + MEDIUM (2)
    """
    total_severity = 0
    for alert in alerts:
        severity = ALERT_SEVERITY_MAP.get(alert, AlertSeverity.LOW)
        total_severity += severity.value
    return total_severity


def prioritize_alert(transaction: dict, alerts: List[str]) -> Tuple[AlertPriority, Dict]:
    """
    Determine the priority level for a transaction's alerts.
    
    Priority is calculated based on:
    1. Risk category (FRAUD > SUSPICIOUS > SAFE)
    2. Number of alerts triggered
    3. Total severity score of alerts
    
    Priority Rules:
    - CRITICAL: FRAUD category with 2+ alerts OR 3+ alerts with high severity
    - HIGH: FRAUD category with 1 alert OR SUSPICIOUS with 3+ alerts OR high severity score (≥6)
    - MEDIUM: SUSPICIOUS category with 1-2 alerts OR moderate severity score (3-5)
    - LOW: Any other alert conditions
    
    Args:
        transaction (dict): Transaction data containing risk_category
        alerts (List[str]): List of triggered alerts
    
    Returns:
        Tuple[AlertPriority, Dict]: Priority level and metadata about the prioritization
            Metadata includes:
            - alert_count: Number of alerts
            - severity_score: Total severity score
            - risk_category: Transaction risk category
            - priority_reason: Explanation of priority assignment
    
    Example:
        >>> transaction = {'risk_category': 'FRAUD'}
        >>> alerts = ['PRICE_ANOMALY', 'HIGH_RISK_COMPANY']
        >>> priority, metadata = prioritize_alert(transaction, alerts)
        >>> priority
        <AlertPriority.CRITICAL: 4>
    """
    if not alerts:
        return AlertPriority.LOW, {
            'alert_count': 0,
            'severity_score': 0,
            'risk_category': transaction.get('risk_category', 'UNKNOWN'),
            'priority_reason': 'No alerts triggered'
        }
    
    risk_category = transaction.get('risk_category', 'SUSPICIOUS')
    alert_count = len(alerts)
    severity_score = calculate_alert_severity_score(alerts)
    
    # Determine priority based on rules
    priority = AlertPriority.LOW
    reason = ""
    
    if risk_category == 'FRAUD':
        if alert_count >= 2:
            priority = AlertPriority.CRITICAL
            reason = f"FRAUD category with {alert_count} alerts"
        else:
            priority = AlertPriority.HIGH
            reason = f"FRAUD category with {alert_count} alert"
    elif alert_count >= 3:
        if severity_score >= 6:
            priority = AlertPriority.CRITICAL
            reason = f"{alert_count} alerts with high severity score ({severity_score})"
        elif risk_category == 'SUSPICIOUS':
            priority = AlertPriority.HIGH
            reason = f"SUSPICIOUS category with {alert_count} alerts"
        else:
            priority = AlertPriority.MEDIUM
            reason = f"{alert_count} alerts with moderate severity"
    elif severity_score >= 6:
        priority = AlertPriority.HIGH
        reason = f"High severity score ({severity_score})"
    elif risk_category == 'SUSPICIOUS':
        if alert_count >= 1:
            priority = AlertPriority.MEDIUM
            reason = f"SUSPICIOUS category with {alert_count} alert(s)"
        else:
            priority = AlertPriority.LOW
            reason = "SUSPICIOUS category with no specific alerts"
    else:
        priority = AlertPriority.LOW
        reason = f"Low risk with {alert_count} alert(s)"
    
    metadata = {
        'alert_count': alert_count,
        'severity_score': severity_score,
        'risk_category': risk_category,
        'priority_reason': reason
    }
    
    return priority, metadata


def get_prioritized_alerts(transactions: List[dict]) -> List[Dict]:
    """
    Process multiple transactions and return them sorted by alert priority.
    
    This function checks alerts for each transaction, calculates priority,
    and returns a sorted list with the highest priority alerts first.
    
    Args:
        transactions (List[dict]): List of transaction dictionaries
    
    Returns:
        List[Dict]: Sorted list of transactions with alert information
            Each item contains:
            - transaction: Original transaction data
            - alerts: List of triggered alerts
            - priority: AlertPriority enum value
            - priority_level: String representation of priority
            - metadata: Prioritization metadata
    
    Example:
        >>> transactions = [
        ...     {'transaction_id': 'TXN001', 'risk_category': 'FRAUD', 
        ...      'price_deviation': 0.6, 'route_anomaly': 1, 
        ...      'company_risk_score': 0.9, 'port_activity_index': 1.2},
        ...     {'transaction_id': 'TXN002', 'risk_category': 'SUSPICIOUS',
        ...      'price_deviation': 0.3, 'route_anomaly': 0,
        ...      'company_risk_score': 0.5, 'port_activity_index': 1.0}
        ... ]
        >>> prioritized = get_prioritized_alerts(transactions)
        >>> prioritized[0]['priority_level']
        'CRITICAL'
    """
    prioritized_transactions = []
    
    for transaction in transactions:
        # Check alerts for this transaction
        alerts = check_alerts(transaction)
        
        # Only include transactions with alerts
        if alerts:
            priority, metadata = prioritize_alert(transaction, alerts)
            
            prioritized_transactions.append({
                'transaction': transaction,
                'alerts': alerts,
                'priority': priority,
                'priority_level': priority.name,
                'priority_value': priority.value,
                'metadata': metadata
            })
    
    # Sort by priority value (descending) - highest priority first
    prioritized_transactions.sort(key=lambda x: x['priority_value'], reverse=True)
    
    return prioritized_transactions


def get_alerts_by_priority(transactions: List[dict], 
                           min_priority: AlertPriority = AlertPriority.LOW) -> List[Dict]:
    """
    Filter transactions to only include those meeting a minimum priority level.
    
    Args:
        transactions (List[dict]): List of transaction dictionaries
        min_priority (AlertPriority): Minimum priority level to include
    
    Returns:
        List[Dict]: Filtered and sorted list of high-priority alerts
    
    Example:
        >>> transactions = [...]
        >>> critical_alerts = get_alerts_by_priority(transactions, AlertPriority.CRITICAL)
        >>> high_and_critical = get_alerts_by_priority(transactions, AlertPriority.HIGH)
    """
    all_prioritized = get_prioritized_alerts(transactions)
    
    # Filter by minimum priority
    filtered = [
        alert_info for alert_info in all_prioritized
        if alert_info['priority_value'] >= min_priority.value
    ]
    
    return filtered


class AlertStore:
    """
    In-memory storage for alerts and alert summaries.

    This class provides a simple persistence layer for the alert system,
    storing alerts during runtime without requiring a database. It supports
    storing, retrieving, and filtering alerts by various criteria.

    Thread-safe for concurrent access using a simple locking mechanism.

    Attributes:
        _alerts (Dict[str, List[Alert]]): Alerts indexed by transaction_id
        _summaries (Dict[str, AlertSummary]): Alert summaries indexed by transaction_id
        _lock: Threading lock for thread-safe operations
    """

    def __init__(self):
        """Initialize the alert store with empty storage."""
        from threading import Lock
        self._alerts: Dict[str, List[Alert]] = {}
        self._summaries: Dict[str, AlertSummary] = {}
        self._lock = Lock()

    def store_alert(self, alert: Alert) -> None:
        """
        Store a single alert.

        Args:
            alert (Alert): Alert object to store

        Example:
            >>> store = AlertStore()
            >>> alert = Alert(transaction_id='TXN001', alert_type='PRICE_ANOMALY',
            ...               severity=AlertSeverity.HIGH)
            >>> store.store_alert(alert)
        """
        with self._lock:
            transaction_id = alert.transaction_id
            if transaction_id not in self._alerts:
                self._alerts[transaction_id] = []
            self._alerts[transaction_id].append(alert)

    def store_alerts(self, alerts: List[Alert]) -> None:
        """
        Store multiple alerts at once.

        Args:
            alerts (List[Alert]): List of Alert objects to store

        Example:
            >>> store = AlertStore()
            >>> alerts = [Alert(...), Alert(...)]
            >>> store.store_alerts(alerts)
        """
        for alert in alerts:
            self.store_alert(alert)

    def store_summary(self, summary: AlertSummary) -> None:
        """
        Store an alert summary.

        Args:
            summary (AlertSummary): AlertSummary object to store

        Example:
            >>> store = AlertStore()
            >>> summary = AlertSummary(...)
            >>> store.store_summary(summary)
        """
        with self._lock:
            self._summaries[summary.transaction_id] = summary

    def get_alerts_by_transaction(self, transaction_id: str) -> List[Alert]:
        """
        Retrieve all alerts for a specific transaction.

        Args:
            transaction_id (str): Transaction ID to retrieve alerts for

        Returns:
            List[Alert]: List of alerts for the transaction (empty if none found)

        Example:
            >>> store = AlertStore()
            >>> alerts = store.get_alerts_by_transaction('TXN001')
        """
        with self._lock:
            return self._alerts.get(transaction_id, []).copy()

    def get_summary_by_transaction(self, transaction_id: str) -> Optional[AlertSummary]:
        """
        Retrieve alert summary for a specific transaction.

        Args:
            transaction_id (str): Transaction ID to retrieve summary for

        Returns:
            Optional[AlertSummary]: AlertSummary if found, None otherwise

        Example:
            >>> store = AlertStore()
            >>> summary = store.get_summary_by_transaction('TXN001')
        """
        with self._lock:
            return self._summaries.get(transaction_id)

    def get_alerts_by_priority(self, priority: AlertPriority) -> List[AlertSummary]:
        """
        Retrieve all alert summaries with a specific priority level.

        Args:
            priority (AlertPriority): Priority level to filter by

        Returns:
            List[AlertSummary]: List of alert summaries matching the priority

        Example:
            >>> store = AlertStore()
            >>> critical_alerts = store.get_alerts_by_priority(AlertPriority.CRITICAL)
        """
        with self._lock:
            return [
                summary for summary in self._summaries.values()
                if summary.priority == priority
            ]

    def get_alerts_by_min_priority(self, min_priority: AlertPriority) -> List[AlertSummary]:
        """
        Retrieve all alert summaries with priority at or above the specified level.

        Args:
            min_priority (AlertPriority): Minimum priority level

        Returns:
            List[AlertSummary]: List of alert summaries with priority >= min_priority,
                               sorted by priority (highest first)

        Example:
            >>> store = AlertStore()
            >>> high_priority_alerts = store.get_alerts_by_min_priority(AlertPriority.HIGH)
        """
        with self._lock:
            filtered = [
                summary for summary in self._summaries.values()
                if summary.priority.value >= min_priority.value
            ]
            # Sort by priority value (descending)
            filtered.sort(key=lambda s: s.priority.value, reverse=True)
            return filtered

    def get_alerts_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Alert]:
        """
        Retrieve all alerts within a specific time range.

        Args:
            start_time (datetime): Start of time range (inclusive)
            end_time (datetime): End of time range (inclusive)

        Returns:
            List[Alert]: List of alerts within the time range, sorted by timestamp

        Example:
            >>> from datetime import datetime, timedelta
            >>> store = AlertStore()
            >>> now = datetime.now()
            >>> recent_alerts = store.get_alerts_by_time_range(
            ...     now - timedelta(hours=1), now
            ... )
        """
        with self._lock:
            all_alerts = []
            for alerts_list in self._alerts.values():
                for alert in alerts_list:
                    if start_time <= alert.timestamp <= end_time:
                        all_alerts.append(alert)
            # Sort by timestamp
            all_alerts.sort(key=lambda a: a.timestamp)
            return all_alerts

    def get_all_alerts(self) -> List[Alert]:
        """
        Retrieve all stored alerts.

        Returns:
            List[Alert]: List of all alerts, sorted by timestamp (newest first)

        Example:
            >>> store = AlertStore()
            >>> all_alerts = store.get_all_alerts()
        """
        with self._lock:
            all_alerts = []
            for alerts_list in self._alerts.values():
                all_alerts.extend(alerts_list)
            # Sort by timestamp (newest first)
            all_alerts.sort(key=lambda a: a.timestamp, reverse=True)
            return all_alerts

    def get_all_summaries(self) -> List[AlertSummary]:
        """
        Retrieve all stored alert summaries.

        Returns:
            List[AlertSummary]: List of all summaries, sorted by priority (highest first)

        Example:
            >>> store = AlertStore()
            >>> all_summaries = store.get_all_summaries()
        """
        with self._lock:
            summaries = list(self._summaries.values())
            # Sort by priority value (descending)
            summaries.sort(key=lambda s: s.priority.value, reverse=True)
            return summaries

    def get_alert_count(self) -> int:
        """
        Get the total number of alerts stored.

        Returns:
            int: Total number of alerts

        Example:
            >>> store = AlertStore()
            >>> count = store.get_alert_count()
        """
        with self._lock:
            return sum(len(alerts) for alerts in self._alerts.values())

    def get_summary_count(self) -> int:
        """
        Get the total number of alert summaries stored.

        Returns:
            int: Total number of summaries

        Example:
            >>> store = AlertStore()
            >>> count = store.get_summary_count()
        """
        with self._lock:
            return len(self._summaries)

    def get_transaction_ids(self) -> List[str]:
        """
        Get all transaction IDs that have alerts.

        Returns:
            List[str]: List of transaction IDs with alerts

        Example:
            >>> store = AlertStore()
            >>> transaction_ids = store.get_transaction_ids()
        """
        with self._lock:
            return list(self._alerts.keys())

    def clear(self) -> None:
        """
        Clear all stored alerts and summaries.

        Useful for testing or resetting the system.

        Example:
            >>> store = AlertStore()
            >>> store.clear()
        """
        with self._lock:
            self._alerts.clear()
            self._summaries.clear()

    def get_statistics(self) -> Dict:
        """
        Get statistics about stored alerts.

        Returns:
            Dict: Statistics including counts by priority, severity, and type

        Example:
            >>> store = AlertStore()
            >>> stats = store.get_statistics()
            >>> print(stats['total_alerts'])
        """
        with self._lock:
            stats = {
                'total_alerts': self.get_alert_count(),
                'total_summaries': self.get_summary_count(),
                'total_transactions': len(self._alerts),
                'priority_counts': {
                    'CRITICAL': 0,
                    'HIGH': 0,
                    'MEDIUM': 0,
                    'LOW': 0
                },
                'alert_type_counts': {}
            }

            # Count by priority
            for summary in self._summaries.values():
                stats['priority_counts'][summary.priority.name] += 1

            # Count by alert type
            for alerts_list in self._alerts.values():
                for alert in alerts_list:
                    alert_type = alert.alert_type
                    stats['alert_type_counts'][alert_type] = \
                        stats['alert_type_counts'].get(alert_type, 0) + 1

            return stats


# Global alert store instance for easy access
_global_alert_store = None


def get_alert_store() -> AlertStore:
    """
    Get the global AlertStore instance (singleton pattern).

    Returns:
        AlertStore: Global alert store instance

    Example:
        >>> store = get_alert_store()
        >>> store.store_alert(alert)
    """
    global _global_alert_store
    if _global_alert_store is None:
        _global_alert_store = AlertStore()
    return _global_alert_store


def reset_alert_store() -> None:
    """
    Reset the global alert store (useful for testing).

    Example:
        >>> reset_alert_store()
    """
    global _global_alert_store
    _global_alert_store = None



class AlertStore:
    """
    In-memory storage for alerts and alert summaries.
    
    This class provides a simple persistence layer for the alert system,
    storing alerts during runtime without requiring a database. It supports
    storing, retrieving, and filtering alerts by various criteria.
    
    Thread-safe for concurrent access using a simple locking mechanism.
    
    Attributes:
        _alerts (Dict[str, List[Alert]]): Alerts indexed by transaction_id
        _summaries (Dict[str, AlertSummary]): Alert summaries indexed by transaction_id
        _lock: Threading lock for thread-safe operations
    """
    
    def __init__(self):
        """Initialize the alert store with empty storage."""
        from threading import Lock
        self._alerts: Dict[str, List[Alert]] = {}
        self._summaries: Dict[str, AlertSummary] = {}
        self._lock = Lock()
    
    def store_alert(self, alert: Alert) -> None:
        """
        Store a single alert.
        
        Args:
            alert (Alert): Alert object to store
        
        Example:
            >>> store = AlertStore()
            >>> alert = Alert(transaction_id='TXN001', alert_type='PRICE_ANOMALY', 
            ...               severity=AlertSeverity.HIGH)
            >>> store.store_alert(alert)
        """
        with self._lock:
            transaction_id = alert.transaction_id
            if transaction_id not in self._alerts:
                self._alerts[transaction_id] = []
            self._alerts[transaction_id].append(alert)
    
    def store_alerts(self, alerts: List[Alert]) -> None:
        """
        Store multiple alerts at once.
        
        Args:
            alerts (List[Alert]): List of Alert objects to store
        
        Example:
            >>> store = AlertStore()
            >>> alerts = [Alert(...), Alert(...)]
            >>> store.store_alerts(alerts)
        """
        for alert in alerts:
            self.store_alert(alert)
    
    def store_summary(self, summary: AlertSummary) -> None:
        """
        Store an alert summary.
        
        Args:
            summary (AlertSummary): AlertSummary object to store
        
        Example:
            >>> store = AlertStore()
            >>> summary = AlertSummary(...)
            >>> store.store_summary(summary)
        """
        with self._lock:
            self._summaries[summary.transaction_id] = summary
    
    def get_alerts_by_transaction(self, transaction_id: str) -> List[Alert]:
        """
        Retrieve all alerts for a specific transaction.
        
        Args:
            transaction_id (str): Transaction ID to retrieve alerts for
        
        Returns:
            List[Alert]: List of alerts for the transaction (empty if none found)
        
        Example:
            >>> store = AlertStore()
            >>> alerts = store.get_alerts_by_transaction('TXN001')
        """
        with self._lock:
            return self._alerts.get(transaction_id, []).copy()
    
    def get_summary_by_transaction(self, transaction_id: str) -> Optional[AlertSummary]:
        """
        Retrieve alert summary for a specific transaction.
        
        Args:
            transaction_id (str): Transaction ID to retrieve summary for
        
        Returns:
            Optional[AlertSummary]: AlertSummary if found, None otherwise
        
        Example:
            >>> store = AlertStore()
            >>> summary = store.get_summary_by_transaction('TXN001')
        """
        with self._lock:
            return self._summaries.get(transaction_id)
    
    def get_alerts_by_priority(self, priority: AlertPriority) -> List[AlertSummary]:
        """
        Retrieve all alert summaries with a specific priority level.
        
        Args:
            priority (AlertPriority): Priority level to filter by
        
        Returns:
            List[AlertSummary]: List of alert summaries matching the priority
        
        Example:
            >>> store = AlertStore()
            >>> critical_alerts = store.get_alerts_by_priority(AlertPriority.CRITICAL)
        """
        with self._lock:
            return [
                summary for summary in self._summaries.values()
                if summary.priority == priority
            ]
    
    def get_alerts_by_min_priority(self, min_priority: AlertPriority) -> List[AlertSummary]:
        """
        Retrieve all alert summaries with priority at or above the specified level.
        
        Args:
            min_priority (AlertPriority): Minimum priority level
        
        Returns:
            List[AlertSummary]: List of alert summaries with priority >= min_priority,
                               sorted by priority (highest first)
        
        Example:
            >>> store = AlertStore()
            >>> high_priority_alerts = store.get_alerts_by_min_priority(AlertPriority.HIGH)
        """
        with self._lock:
            filtered = [
                summary for summary in self._summaries.values()
                if summary.priority.value >= min_priority.value
            ]
            # Sort by priority value (descending)
            filtered.sort(key=lambda s: s.priority.value, reverse=True)
            return filtered
    
    def get_alerts_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Alert]:
        """
        Retrieve all alerts within a specific time range.
        
        Args:
            start_time (datetime): Start of time range (inclusive)
            end_time (datetime): End of time range (inclusive)
        
        Returns:
            List[Alert]: List of alerts within the time range, sorted by timestamp
        
        Example:
            >>> from datetime import datetime, timedelta
            >>> store = AlertStore()
            >>> now = datetime.now()
            >>> recent_alerts = store.get_alerts_by_time_range(
            ...     now - timedelta(hours=1), now
            ... )
        """
        with self._lock:
            all_alerts = []
            for alerts_list in self._alerts.values():
                for alert in alerts_list:
                    if start_time <= alert.timestamp <= end_time:
                        all_alerts.append(alert)
            # Sort by timestamp
            all_alerts.sort(key=lambda a: a.timestamp)
            return all_alerts
    
    def get_all_alerts(self) -> List[Alert]:
        """
        Retrieve all stored alerts.
        
        Returns:
            List[Alert]: List of all alerts, sorted by timestamp (newest first)
        
        Example:
            >>> store = AlertStore()
            >>> all_alerts = store.get_all_alerts()
        """
        with self._lock:
            all_alerts = []
            for alerts_list in self._alerts.values():
                all_alerts.extend(alerts_list)
            # Sort by timestamp (newest first)
            all_alerts.sort(key=lambda a: a.timestamp, reverse=True)
            return all_alerts
    
    def get_all_summaries(self) -> List[AlertSummary]:
        """
        Retrieve all stored alert summaries.
        
        Returns:
            List[AlertSummary]: List of all summaries, sorted by priority (highest first)
        
        Example:
            >>> store = AlertStore()
            >>> all_summaries = store.get_all_summaries()
        """
        with self._lock:
            summaries = list(self._summaries.values())
            # Sort by priority value (descending)
            summaries.sort(key=lambda s: s.priority.value, reverse=True)
            return summaries
    
    def get_alert_count(self) -> int:
        """
        Get the total number of alerts stored.
        
        Returns:
            int: Total number of alerts
        
        Example:
            >>> store = AlertStore()
            >>> count = store.get_alert_count()
        """
        with self._lock:
            return sum(len(alerts) for alerts in self._alerts.values())
    
    def get_summary_count(self) -> int:
        """
        Get the total number of alert summaries stored.
        
        Returns:
            int: Total number of summaries
        
        Example:
            >>> store = AlertStore()
            >>> count = store.get_summary_count()
        """
        with self._lock:
            return len(self._summaries)
    
    def get_transaction_ids(self) -> List[str]:
        """
        Get all transaction IDs that have alerts.
        
        Returns:
            List[str]: List of transaction IDs with alerts
        
        Example:
            >>> store = AlertStore()
            >>> transaction_ids = store.get_transaction_ids()
        """
        with self._lock:
            return list(self._alerts.keys())
    
    def clear(self) -> None:
        """
        Clear all stored alerts and summaries.
        
        Useful for testing or resetting the system.
        
        Example:
            >>> store = AlertStore()
            >>> store.clear()
        """
        with self._lock:
            self._alerts.clear()
            self._summaries.clear()
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about stored alerts.
        
        Returns:
            Dict: Statistics including counts by priority, severity, and type
        
        Example:
            >>> store = AlertStore()
            >>> stats = store.get_statistics()
            >>> print(stats['total_alerts'])
        """
        with self._lock:
            stats = {
                'total_alerts': self.get_alert_count(),
                'total_summaries': self.get_summary_count(),
                'total_transactions': len(self._alerts),
                'priority_counts': {
                    'CRITICAL': 0,
                    'HIGH': 0,
                    'MEDIUM': 0,
                    'LOW': 0
                },
                'alert_type_counts': {},
                'dismissed_count': 0,
                'active_count': 0
            }
            
            # Count by priority and dismissed status
            for summary in self._summaries.values():
                stats['priority_counts'][summary.priority.name] += 1
                if summary.dismissed:
                    stats['dismissed_count'] += 1
                else:
                    stats['active_count'] += 1
            
            # Count by alert type
            for alerts_list in self._alerts.values():
                for alert in alerts_list:
                    alert_type = alert.alert_type
                    stats['alert_type_counts'][alert_type] = \
                        stats['alert_type_counts'].get(alert_type, 0) + 1
            
            return stats
    
    def dismiss_alert_summary(self, transaction_id: str, dismissed_by: str = "analyst") -> bool:
        """
        Dismiss an alert summary for a transaction.
        
        Args:
            transaction_id (str): Transaction ID to dismiss alerts for
            dismissed_by (str): User who dismissed the alert (default: "analyst")
        
        Returns:
            bool: True if alert was dismissed, False if not found
        
        Example:
            >>> store = AlertStore()
            >>> store.dismiss_alert_summary('TXN001', 'john.doe')
        """
        with self._lock:
            summary = self._summaries.get(transaction_id)
            if summary:
                summary.dismissed = True
                summary.dismissed_at = datetime.now()
                summary.dismissed_by = dismissed_by
                
                # Also mark all individual alerts as dismissed
                if transaction_id in self._alerts:
                    for alert in self._alerts[transaction_id]:
                        alert.dismissed = True
                        alert.dismissed_at = datetime.now()
                        alert.dismissed_by = dismissed_by
                
                return True
            return False
    
    def undismiss_alert_summary(self, transaction_id: str) -> bool:
        """
        Undismiss (restore) an alert summary for a transaction.
        
        Args:
            transaction_id (str): Transaction ID to undismiss alerts for
        
        Returns:
            bool: True if alert was undismissed, False if not found
        
        Example:
            >>> store = AlertStore()
            >>> store.undismiss_alert_summary('TXN001')
        """
        with self._lock:
            summary = self._summaries.get(transaction_id)
            if summary:
                summary.dismissed = False
                summary.dismissed_at = None
                summary.dismissed_by = None
                
                # Also undismiss all individual alerts
                if transaction_id in self._alerts:
                    for alert in self._alerts[transaction_id]:
                        alert.dismissed = False
                        alert.dismissed_at = None
                        alert.dismissed_by = None
                
                return True
            return False
    
    def get_active_summaries(self) -> List[AlertSummary]:
        """
        Get all non-dismissed alert summaries.
        
        Returns:
            List[AlertSummary]: List of active (non-dismissed) summaries
        
        Example:
            >>> store = AlertStore()
            >>> active = store.get_active_summaries()
        """
        with self._lock:
            summaries = [s for s in self._summaries.values() if not s.dismissed]
            summaries.sort(key=lambda s: s.priority.value, reverse=True)
            return summaries
    
    def get_dismissed_summaries(self) -> List[AlertSummary]:
        """
        Get all dismissed alert summaries.
        
        Returns:
            List[AlertSummary]: List of dismissed summaries
        
        Example:
            >>> store = AlertStore()
            >>> dismissed = store.get_dismissed_summaries()
        """
        with self._lock:
            summaries = [s for s in self._summaries.values() if s.dismissed]
            summaries.sort(key=lambda s: s.dismissed_at, reverse=True)
            return summaries


# Global alert store instance for easy access
_global_alert_store = None


def get_alert_store() -> AlertStore:
    """
    Get the global AlertStore instance (singleton pattern).
    
    Returns:
        AlertStore: Global alert store instance
    
    Example:
        >>> store = get_alert_store()
        >>> store.store_alert(alert)
    """
    global _global_alert_store
    if _global_alert_store is None:
        _global_alert_store = AlertStore()
    return _global_alert_store


def reset_alert_store() -> None:
    """
    Reset the global alert store (useful for testing).
    
    Example:
        >>> reset_alert_store()
    """
    global _global_alert_store
    _global_alert_store = None
