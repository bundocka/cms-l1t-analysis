from cmsl1t.math import cumulative_sum_and_error


def cumulative_hist(hist, suffix='_cumul'):
    h = hist.clone(hist.name + suffix)
    values, errors = cumulative_sum_and_error(hist)
    h.set_content(values)
    h.set_error(errors)
    return h


def normalise_to_collision_rate(hist, collision_rate=4.0e7):
    first_bin = hist.get_bin_content(1)
    if first_bin != 0:
        hist.GetSumw2()
        hist.Scale(40000000/92000)#collision_rate / first_bin)
    return hist


def normalise_to_unit_area(histograms):
    for hist in histograms:
        if hist.integral() != 0:
            yield hist / hist.integral()
        else:
            yield hist.Clone()
