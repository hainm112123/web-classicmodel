export type Summary = {
  customers: number;
  orders: number;
  salesRevenue: number;
  paymentsReceived: number;
  averageOrderValue: number;
};

export type TimePoint = {
  period: string;
  value: number;
};

export type LabelValue = {
  label: string;
  value: number;
};

export type RecentOrder = {
  orderNumber: number;
  orderDate: string;
  status: string;
  customerName: string;
  total: number;
};

export type CustomerRow = {
  customerNumber: number;
  customerName: string;
  country: string;
  city: string;
  creditLimit: number;
  salesRepEmployeeNumber: number | null;
  salesRepName: string | null;
  orderCount: number;
  salesRevenue: number;
  paymentsReceived: number;
};

export type CustomerDetail = {
  customerNumber: number;
  customerName: string;
  contactName: string;
  phone: string;
  country: string;
  city: string;
  state: string | null;
  creditLimit: number;
  salesRepName: string | null;
  orderCount: number;
  salesRevenue: number;
  paymentsReceived: number;
  outstandingBalance: number;
};

export type CustomerOrder = {
  orderNumber: number;
  orderDate: string;
  status: string;
  total: number;
};

export type CustomerPayment = {
  checkNumber: string;
  paymentDate: string;
  amount: number;
};

export type OrderRow = {
  orderNumber: number;
  orderDate: string;
  requiredDate: string;
  shippedDate: string | null;
  status: string;
  customerNumber: number;
  customerName: string;
  total: number;
};

export type OrderLine = {
  orderLineNumber: number;
  productCode: string;
  productName: string;
  productLine: string;
  quantityOrdered: number;
  priceEach: number;
  lineTotal: number;
};

export type OrderDetail = {
  orderNumber: number;
  orderDate: string;
  requiredDate: string;
  shippedDate: string | null;
  status: string;
  comments: string | null;
  customer: {
    customerNumber: number;
    customerName: string;
  };
  total: number;
  lines: OrderLine[];
};

export type PaginatedResponse<T> = {
  total: number;
  items: T[];
};

export type LookupResponse = {
  countries: string[];
  cities: string[];
  statuses: string[];
  productLines: string[];
  salesReps: { employeeNumber: number; fullName: string }[];
};

export type PivotResponse = {
  columns: string[];
  rows: { rowKey: string; values: number[]; total: number }[];
};

