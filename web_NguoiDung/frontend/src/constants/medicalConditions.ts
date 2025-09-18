export const MEDICAL_CONDITIONS = [
  'Tăng huyết áp',
  'Tiểu đường type 2',
  'Hen suyễn',
  'Bệnh tim mạch',
  'Cholesterol cao',
  'Viêm khớp',
  'Đau nửa đầu',
  'Rối loạn giấc ngủ',
  'Bệnh gan',
  'Bệnh thận',
  'Loãng xương',
  'Trầm cảm',
  'Lo âu',
  'Dạ dày tá tràng',
  'Viêm đại tràng',
] as const;

export const SMOKING_OPTIONS = [
  { value: 'never', label: 'Không bao giờ' },
  { value: 'former', label: 'Đã từng hút' },
  { value: 'current', label: 'Đang hút thuốc' },
] as const;

export const DRINKING_OPTIONS = [
  { value: 'never', label: 'Không bao giờ' },
  { value: 'occasional', label: 'Thỉnh thoảng' },
  { value: 'frequent', label: 'Thường xuyên' },
] as const;
