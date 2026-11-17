import { zodResolver } from "@hookform/resolvers/zod";
import { router } from "expo-router";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { Modal, Pressable, Text, TextInput, View } from "react-native";
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
  memberId: z.string().min(1, "Select a member."),
  categoryId: z.string().min(1, "Select a category."),
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
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      type: "expense",
      amount: "",
      date: new Date().toISOString().slice(0, 10),
      merchant: "",
        memberId: "",
        categoryId: "",
    },
  });

  const [error, setError] = useState<Error>();
  const [categoryOpen, setCategoryOpen] = useState(false);
  const type = watch("type");
  const memberId = watch("memberId");
  const categoryId = watch("categoryId");

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      const body = {
        member_id: values.memberId,
        category_id: values.categoryId,
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

      <View style={styles.chipRow}>
        {(["expense", "income"] as const).map((value) => (
          <Pressable key={value} onPress={() => { setValue("type", value); setValue("categoryId", ""); }} style={[styles.chip, type === value && styles.selectedChip]}>
            <Text style={styles.chipText}>{value === "income" ? "Income" : "Expense"}</Text>
          </Pressable>
        ))}
      </View>

      <FieldLabel>Household member</FieldLabel>
      <View style={styles.chipRow}>
        {members.data?.map((member) => (
          <Pressable key={member.id} onPress={() => setValue("memberId", member.id)} style={[styles.chip, memberId === member.id && styles.selectedChip]}>
            <Text style={styles.chipText}>{member.display_name}</Text>
          </Pressable>
        ))}
      </View>
      {errors.memberId && <Text style={styles.error}>{errors.memberId.message}</Text>}

      <FieldLabel>Category</FieldLabel>
      <Pressable accessibilityRole="button" accessibilityLabel="Choose category" onPress={() => setCategoryOpen(true)} style={styles.input}>
        <Text style={categoryId ? styles.chipText : styles.muted}>{categories.data?.find((category) => category.id === categoryId)?.name ?? "Select a category"}</Text>
      </Pressable>
      <Modal visible={categoryOpen} transparent animationType="slide" onRequestClose={() => setCategoryOpen(false)}>
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <Text style={styles.title}>Choose category</Text>
            {(categories.data ?? []).filter((category) => category.category_type === type || category.category_type === "other").map((category) => (
              <Pressable key={category.id} onPress={() => { setValue("categoryId", category.id); setCategoryOpen(false); }} style={styles.modalOption}>
                <Text style={styles.chipText}>{category.name}</Text>
              </Pressable>
            ))}
            <ActionButton title="Cancel" secondary onPress={() => setCategoryOpen(false)} />
          </View>
        </View>
      </Modal>
      {errors.categoryId && <Text style={styles.error}>{errors.categoryId.message}</Text>}

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
