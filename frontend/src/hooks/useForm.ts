import { useState, useCallback } from 'react';

interface FormField {
  value: any;
  touched: boolean;
  error: string | null;
}

interface FormFields {
  [key: string]: FormField;
}

interface UseFormOptions {
  initialValues: { [key: string]: any };
  validate?: (values: { [key: string]: any }) => { [key: string]: string };
  onSubmit: (values: { [key: string]: any }) => void | Promise<void>;
}

export function useForm(options: UseFormOptions) {
  const [fields, setFields] = useState<FormFields>(() => {
    const initial: FormFields = {};
    Object.keys(options.initialValues).forEach(key => {
      initial[key] = {
        value: options.initialValues[key],
        touched: false,
        error: null,
      };
    });
    return initial;
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = useCallback((fieldName: string, value: any) => {
    setFields(prev => ({
      ...prev,
      [fieldName]: {
        ...prev[fieldName],
        value,
      },
    }));
  }, []);

  const handleBlur = useCallback((fieldName: string) => {
    setFields(prev => {
      const updated = { ...prev };
      updated[fieldName] = {
        ...updated[fieldName],
        touched: true,
      };

      // Validar al blur si existe función de validación
      if (options.validate) {
        const values = Object.keys(updated).reduce((acc, key) => {
          acc[key] = updated[key].value;
          return acc;
        }, {} as { [key: string]: any });

        const errors = options.validate(values);
        if (errors[fieldName]) {
          updated[fieldName].error = errors[fieldName];
        } else {
          updated[fieldName].error = null;
        }
      }

      return updated;
    });
  }, [options]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();

      // Mark all as touched
      setFields(prev => {
        const updated = { ...prev };
        Object.keys(updated).forEach(key => {
          updated[key].touched = true;
        });
        return updated;
      });

      // Validar
      if (options.validate) {
        const values = Object.keys(fields).reduce((acc, key) => {
          acc[key] = fields[key].value;
          return acc;
        }, {} as { [key: string]: any });

        const errors = options.validate(values);

        setFields(prev => {
          const updated = { ...prev };
          Object.keys(errors).forEach(key => {
            if (updated[key]) {
              updated[key].error = errors[key];
            }
          });
          return updated;
        });

        // Si hay errores, no enviar
        if (Object.keys(errors).length > 0) {
          return;
        }
      }

      setIsSubmitting(true);
      try {
        const values = Object.keys(fields).reduce((acc, key) => {
          acc[key] = fields[key].value;
          return acc;
        }, {} as { [key: string]: any });

        await options.onSubmit(values);
      } finally {
        setIsSubmitting(false);
      }
    },
    [fields, options]
  );

  const reset = useCallback(() => {
    const initial: FormFields = {};
    Object.keys(options.initialValues).forEach(key => {
      initial[key] = {
        value: options.initialValues[key],
        touched: false,
        error: null,
      };
    });
    setFields(initial);
  }, [options.initialValues]);

  const getFieldProps = useCallback((fieldName: string) => {
    const field = fields[fieldName];
    return {
      value: field.value,
      onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
        handleChange(fieldName, e.target.value),
      onBlur: () => handleBlur(fieldName),
      error: field.touched ? field.error : null,
    };
  }, [fields, handleChange, handleBlur]);

  const setFieldValue = useCallback((fieldName: string, value: any) => {
    handleChange(fieldName, value);
  }, [handleChange]);

  const setFieldError = useCallback((fieldName: string, error: string | null) => {
    setFields(prev => ({
      ...prev,
      [fieldName]: {
        ...prev[fieldName],
        error,
      },
    }));
  }, []);

  return {
    fields,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    getFieldProps,
    setFieldValue,
    setFieldError,
    reset,
  };
}
