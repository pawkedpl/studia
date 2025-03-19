package org.example;

import java.util.LinkedList;
import java.util.Queue;
import java.util.Stack;

public class zad1 {
    public static void main(String[] args) {
        // Implementacja kolejki FIFO
        Queue<Integer> fifoQueue = new LinkedList<>();

        // Dodawanie 50 elementów do kolejki FIFO
        for (int i = 1; i <= 50; i++) {
            fifoQueue.add(i);
            System.out.println("Dodano do kolejki: " + i);
        }

        // Pobieranie i wypisywanie elementów z kolejki FIFO
        System.out.println("\nElementy pobrane z kolejki FIFO:");
        while (!fifoQueue.isEmpty()) {
            int element = fifoQueue.poll();
            System.out.println("Pobrano z kolejki: " + element);
        }

        // Implementacja stosu LIFO
        Stack<Integer> lifoStack = new Stack<>();

        // Dodawanie 50 elementów do stosu LIFO
        for (int i = 1; i <= 50; i++) {
            lifoStack.push(i);
            System.out.println("Dodano do stosu: " + i);
        }

        // Pobieranie i wypisywanie elementów ze stosu LIFO
        System.out.println("\nElementy pobrane ze stosu LIFO:");
        while (!lifoStack.isEmpty()) {
            int element = lifoStack.pop();
            System.out.println("Pobrano ze stosu: " + element);
        }
    }
}
