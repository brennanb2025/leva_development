import React from "react";
import { useField } from "formik";
import DatePicker from "react-datepicker";

export const DatePickerField = ({ name, value, onChange }) => {
  return (
    <DatePicker
      selected={(value && new Date(value)) || null}
      showTimeSelect
      onChange={val => {
        onChange(name, val);
      }}
      dateFormat="Pp"
      className="stats-input w-fit"
    />
  );
};
