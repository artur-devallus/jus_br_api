export const onlyDigits = (s: string) => {
  return s.replace(/\D/g, "");
}

export const formatCpfOrProcess = (value: string) => {
  const digits = value.replace(/\D/g, "");
  if (digits.length <= 11) {
    // CPF
    return digits
      .replace(/^(\d{3})(\d)/, "$1.$2")
      .replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3")
      .replace(/\.(\d{3})(\d)/, ".$1-$2")
      .slice(0, 14);
  }
  // Processo
  return digits
    .replace(/^(\d{7})(\d)/, "$1-$2")
    .replace(/^(\d{7}-\d{2})(\d{4})(\d)/, "$1.$2.$3")
    .replace(/^(\d{7}-\d{2}\.\d{4}\.\d)(\d{2})(\d{4}).*/, "$1.$2.$3")
    .slice(0, 25);
};
