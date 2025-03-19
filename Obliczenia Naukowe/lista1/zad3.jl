# Pawel Kedzierski 272400

# parametry funkcji: 
#   step - krok, o który zwiększamy wartość początkową podczas iteracji pętli while
#   a - liczba Float64, która jest początkiem przedziału
#   b - liczba Float64, ktora jest końcem przedziału


function is_evenly(step, a::Float64, b::Float64)
    x = a
    y = a

    while x < a + (5 * step)
        println(bitstring(x))
        x += step
        y = nextfloat(y)
    end
end

println(is_evenly(2.0^(-52), 1.0, 2.0))

# parametry funkcji:
#   a - liczba Float64, która jest początkiem przedziału
#   b - liczba Float64, ktora jest końcem przedziału

function is_evenly_but_better(a::Float64, b::Float64)
    last_num = prevfloat(b)
    exp1 = SubString(bitstring(a), 2:12)
    exp2 = SubString(bitstring(last_num), 2:12)

    return exp1 == exp2
end


println("Is evenly distributed? ", is_evenly_but_better(1.0, 2.0))


# parametry funkcji:
#   a - liczba Float64, która jest początkiem przedziału, i z ktorej będzie brana eksponenta
#   b - liczba Float64, ktora jest końcem przedziału


function calculate_step(a::Float64, b::Float64)
    if is_evenly_but_better(a, b)
        exp = SubString(bitstring(a), 2:12)
        exp = parse(Int, exp, base = 2)
        println(exp)
        step::Float64 = (2.0^(exp - 1023) * 2.0^(-52.0))
        return step
    end

    return -1.0
end

println("Calculated step for [0.5, 1] - ", calculate_step(0.5, 1.0))
println("Calculated step for [1, 2] - ", calculate_step(1.0, 2.0))
println("Calculated step for [2, 4] - ", calculate_step(2.0, 4.0))