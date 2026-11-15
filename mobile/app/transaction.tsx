import { zodResolver } from "@hookform/resolvers/zod";
import { router } from "expo-router";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { Text, TextInput } from "react-native";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";
import {
  ActionButton,
  FieldLabel,
  Screen,
  State,
  styles,
} from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";
import { queueTransaction } from "@/lib/offline";
import * as Network from "expo-network";

const schema = z.object({
  type: z.enum(["income", "expense"]),
  amount: z
    .string()
    .trim()
    .refine((value) => Number(value) > 0, "Enter an amount greater than zero."),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Use YYYY-MM-DD."),
  merchant: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

export default function Transaction() {
  const householdId = useHousehold((state) => state.householdId);
  const client = useQueryClient();

  const members = useQuery({
    queryKey: ["members", householdId],
    queryFn: () => api.members(householdId!),
    enabled: Boolean(householdId),
  });

  const categories = useQuery({
    queryKey: ["categories", householdId],
    queryFn: () => api.categories(householdId!),
    enabled: Boolean(householdId),
  });

  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      type: "expense",
      amount: "",
      date: new Date().toISOString().slice(0, 10),
      merchant: "",
    },
  });

  const [error, setError] = useState<Error>();

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      const body = {
        member_id: members.data?.[0]?.id || "",
        category_id: categories.data?.[0]?.id || "",
        transaction_type: values.type,
        amount: values.amount,
        currency: "INR",
        transaction_date: values.date,
        merchant: values.merchant || undefined,
      };

      const state = await Network.getNetworkStateAsync();

      if (state.isConnected !== true) {
        await queueTransaction(body);
        return "offline";
      }

      return api.createTransaction(
        householdId!,
        body,
        `${householdId}-${Date.now()}`,
      );
    },

    onSuccess: async () => {
      await client.invalidateQueries({
        queryKey: ["transactions", householdId],
      });

      router.back();
    },

    onError: (value) =>
      setError(
        value instanceof Error
          ? value
          : new Error("Unable to create transaction."),
      ),
  });

  return (
    <Screen>
      <Text style={styles.title}>Add transaction</Text>

      <Text style={styles.subtitle}>
        The backend validates the member, category, amount, date, and
        transaction type.
      </Text>

      <FieldLabel>Type (income or expense)</FieldLabel>

      <Controller
        control={control}
        name="type"
        render={({ field }) => (
          <TextInput
            style={styles.input}
            value={field.value}
            onChangeText={(value) =>
              field.onChange(value === "income" ? "income" : "expense")
            }
          />
        )}
      />

      {errors.type && <Text style={styles.error}>{errors.type.message}</Text>}

      <FieldLabel>Amount</FieldLabel>

      <Controller
        control={control}
        name="amount"
        render={({ field }) => (
          <TextInput
            style={styles.input}
            keyboardType="decimal-pad"
            value={field.value}
            onChangeText={field.onChange}
            placeholder="0.00"
          />
        )}
      />

      {errors.amount && (
        <Text style={styles.error}>{errors.amount.message}</Text>
      )}

      <FieldLabel>Date</FieldLabel>

      <Controller
        control={control}
        name="date"
        render={({ field }) => (
          <TextInput
            style={styles.input}
            value={field.value}
            onChangeText={field.onChange}
          />
        )}
      />

      {errors.date && <Text style={styles.error}>{errors.date.message}</Text>}

      <FieldLabel>Merchant or description</FieldLabel>

      <Controller
        control={control}
        name="merchant"
        render={({ field }) => (
          <TextInput
            style={styles.input}
            value={field.value}
            onChangeText={field.onChange}
          />
        )}
      />

      <State
        error={error || (members.error as Error) || (categories.error as Error)}
      />

      <ActionButton
        title={
          isSubmitting || mutation.isPending ? "Saving..." : "Save transaction"
        }
        disabled={isSubmitting || mutation.isPending}
        onPress={() =>
          void handleSubmit((values) => mutation.mutateAsync(values))()
        }
      />
    </Screen>
  );
}
